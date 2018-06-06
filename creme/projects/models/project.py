# -*- coding: utf-8 -*-

################################################################################
#    Creme is a free/open-source Customer Relationship Management software
#    Copyright (C) 2009-2018  Hybird
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from django.core.exceptions import ValidationError
from django.db.models import CharField, TextField, ForeignKey, DateTimeField, Max, PROTECT
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.timezone import now, localtime
from django.utils.translation import ugettext_lazy as _, ugettext

from creme.creme_core.constants import DEFAULT_CURRENCY_PK
from creme.creme_core.models import CremeEntity, Currency

from .projectstatus import ProjectStatus


class AbstractProject(CremeEntity):
    name                = CharField(_(u'Name of the project'), max_length=100)
    description         = TextField(_(u'Description'), blank=True)\
                                   .set_tags(optional=True)
    status              = ForeignKey(ProjectStatus, verbose_name=_(u'Status'), on_delete=PROTECT)
    start_date          = DateTimeField(_(u'Estimated start'), blank=True, null=True)\
                                       .set_tags(optional=True)
    end_date            = DateTimeField(_(u'Estimated end'), blank=True, null=True)\
                                       .set_tags(optional=True)
    effective_end_date  = DateTimeField(_(u'Effective end date'), blank=True, null=True)\
                                       .set_tags(optional=True)
    currency            = ForeignKey(Currency, verbose_name=_(u'Currency'),
                                     related_name='+',
                                     default=DEFAULT_CURRENCY_PK, on_delete=PROTECT,
                                    )

    tasks_list = None

    allowed_related = CremeEntity.allowed_related | {'tasks_set'}

    creation_label = _(u'Create a project')
    save_label     = _(u'Save the project')

    class Meta:
        abstract = True
        manager_inheritance_from_future = True
        app_label = 'projects'
        verbose_name = _(u'Project')
        verbose_name_plural = _(u'Projects')
        ordering = ('name',)

    def __unicode__(self) :
        return self.name

    def get_absolute_url(self):
        return reverse('projects__view_project', args=(self.id,))

    @staticmethod
    def get_create_absolute_url():
        return reverse('projects__create_project')

    def get_edit_absolute_url(self):
        return reverse('projects__edit_project', args=(self.id,))

    @staticmethod
    def get_lv_absolute_url():
        return reverse('projects__list_projects')

    def get_html_attrs(self, context):
        attrs = super(AbstractProject, self).get_html_attrs(context)

        # NB: if 'status' if not in the HeaderFilter, it will cause an extra query...
        color = self.status.color_code
        if color:
            attrs['style'] = 'background-color:#{};'.format(color)

        return attrs

    def clean(self):
        super(AbstractProject, self).clean()

        # TODO: refactor if start/end can not be null
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(ugettext(u'Start ({start}) must be before end ({end}).').format(
                                   start=date_format(localtime(self.start_date), 'DATE_FORMAT'),
                                   end=date_format(localtime(self.end_date), 'DATE_FORMAT'),
                                  )
                                 )  # TODO: code & params ??

    # def delete(self):
    def delete(self, *args, **kwargs):
        for task in self.get_tasks():
            # task.delete()
            task.delete(*args, **kwargs)

        # super(AbstractProject, self).delete()
        super(AbstractProject, self).delete(*args, **kwargs)

    def get_tasks(self):
        if self.tasks_list is None:
            self.tasks_list = self.tasks_set.order_by('order')
        return self.tasks_list

    def attribute_order_task(self):
        max_order = self.get_tasks().aggregate(Max('order'))['order__max']
        return (max_order + 1) if max_order is not None else 1

    def get_project_cost(self):
        return sum(task.get_task_cost() for task in self.get_tasks())

    def get_expected_duration(self):  # TODO: not used ??
        return sum(task.safe_duration for task in self.get_tasks())

    def get_effective_duration(self):  # TODO: not used ??
        return sum(task.get_effective_duration() for task in self.get_tasks())

    def get_delay(self):
        return sum(max(0, task.get_delay()) for task in self.get_tasks())

    def close(self):
        """@return Boolean -> False means the project has not been closed (because it is already closed)."""
        if self.effective_end_date:
            already_closed = False
        else:
            already_closed = True
            self.effective_end_date = now()

        return already_closed

    @property
    def is_closed(self):
        return bool(self.effective_end_date)

    def _post_save_clone(self, source):
        from creme.projects.models.task import ProjectTask
        ProjectTask.clone_scope(source.get_tasks(), self)


class Project(AbstractProject):
    class Meta(AbstractProject.Meta):
        swappable = 'PROJECTS_PROJECT_MODEL'
