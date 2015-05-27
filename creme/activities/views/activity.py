# -*- coding: utf-8 -*-

################################################################################
#    Creme is a free/open-source Customer Relationship Management software
#    Copyright (C) 2009-2015  Hybird
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

from datetime import datetime
from functools import partial

from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from creme.creme_core.auth.decorators import login_required, permission_required
from creme.creme_core.auth import EntityCredentials
from creme.creme_core.gui.last_viewed import LastViewedItem
from creme.creme_core.models import CremeEntity, RelationType
from creme.creme_core.utils import get_from_GET_or_404, jsonify
from creme.creme_core.views.generic import view_real_entity, list_view, inner_popup, edit_entity

from creme.persons import get_contact_model
#from creme.persons.models import Contact

from ..constants import (ACTIVITYTYPE_INDISPO, ACTIVITYTYPE_MEETING,
        ACTIVITYTYPE_PHONECALL, ACTIVITYTYPE_TASK,
        REL_SUB_PART_2_ACTIVITY, REL_SUB_ACTIVITY_SUBJECT, REL_SUB_LINKED_2_ACTIVITY)
from ..forms.activity import (ActivityCreateForm, IndisponibilityCreateForm,
        RelatedActivityCreateForm, CalendarActivityCreateForm, ActivityEditForm)
from ..models import Activity, ActivityType, ActivitySubType
from ..utils import get_ical


def _add_activity(request, form_class,
                  content_template='activities/frags/activity_form_content.html',
                  type_id=None, **form_args):
    if request.method == 'POST':
        POST = request.POST
        form = form_class(activity_type_id=type_id, user=request.user, data=POST, **form_args)

        if form.is_valid():
            form.save()
            entity = form_args.get('related_entity', form.instance)

            return redirect(entity)

        cancel_url = POST.get('cancel_url')
    else:
        form = form_class(activity_type_id=type_id, user=request.user, **form_args)
        cancel_url = request.META.get('HTTP_REFERER')

    return render(request, 'activities/add_activity_form.html',
                  {'form':             form,
                   'title':            Activity.get_creation_title(type_id),
                   'content_template': content_template,
                   'submit_label':     _('Save the activity'),
                   'cancel_url':       cancel_url,
                  }
                 )

@login_required
@permission_required(('activities', 'activities.add_activity'))
def add(request):
    return _add_activity(request, ActivityCreateForm)

_TYPES_MAP = {
        "meeting":   ACTIVITYTYPE_MEETING,
        "phonecall": ACTIVITYTYPE_PHONECALL,
        "task":      ACTIVITYTYPE_TASK,
    }

@login_required
@permission_required(('activities', 'activities.add_activity'))
def add_fixedtype(request, act_type):
    type_id = _TYPES_MAP.get(act_type)

    if not type_id:
        raise Http404('No activity type matches with: %s' % act_type)

    return _add_activity(request, ActivityCreateForm, type_id=type_id)

@login_required
@permission_required(('activities', 'activities.add_activity'))
def add_indisponibility(request):
    return _add_activity(request, IndisponibilityCreateForm,
                         content_template='activities/frags/indispo_form_content.html',
                         type_id=ACTIVITYTYPE_INDISPO,
                        )

@login_required
@permission_required(('activities', 'activities.add_activity'))
def add_related(request, entity_id):
    act_type_id = request.GET.get('activity_type')
    entity = get_object_or_404(CremeEntity, pk=entity_id).get_real_entity()

    if act_type_id:
        get_object_or_404(ActivityType, pk=act_type_id)

    request.user.has_perm_to_link_or_die(entity)

#    if isinstance(entity, Contact):
    if isinstance(entity, get_contact_model()):
        rtype_id = REL_SUB_PART_2_ACTIVITY
    else:
        rtype = RelationType.objects.get(pk=REL_SUB_ACTIVITY_SUBJECT)

        if rtype.is_compatible(entity.entity_type_id):
            rtype_id = REL_SUB_ACTIVITY_SUBJECT
        else:
            rtype_id = REL_SUB_LINKED_2_ACTIVITY #not custom, & all ContentTypes should be accepted

    return _add_activity(request, RelatedActivityCreateForm,
                         related_entity=entity,
                         relation_type_id=rtype_id,
                         type_id=act_type_id,
                        )

@login_required
@permission_required(('activities', 'activities.add_activity'))
def add_popup(request):
    if request.method == 'POST':
        form = CalendarActivityCreateForm(user=request.user, data=request.POST,
                                          files=request.FILES or None,
                                         )

        if form.is_valid():
            form.save()
    else:
        get_or_404 = partial(get_from_GET_or_404, GET=request.GET, cast=int)
        today = datetime.today()
        start_date = datetime(get_or_404(key='year',   default=today.year),
                              get_or_404(key='month',  default=today.month),
                              get_or_404(key='day',    default=today.day),
                              get_or_404(key='hour',   default=today.hour),
                              get_or_404(key='minute', default=today.minute),
                             )
        form = CalendarActivityCreateForm(start=start_date, user=request.user)

    return inner_popup(request, 'activities/add_popup_activity_form.html',
                       {'form':   form,
                        'title':  _(u'New activity'),
                        #TODO: content_template ?? (see template)
                       },
                       is_valid=form.is_valid(),
                       reload=False,
                       delegate_reload=True,
                      )

@login_required
@permission_required('activities')
def edit(request, activity_id):
    return edit_entity(request, activity_id, Activity, ActivityEditForm)

@login_required
@permission_required('activities')
def detailview(request, activity_id):
    #return view_real_entity(request, activity_id, '/activities/activity',
                            #'activities/view_activity.html',
                           #)

    #TODO: this hack should be useless (ProjectTask do not inherit from Activity) => view_entity()
    #TODO: create a generic view ? add this featue to _the_ generic detailview ??
    entity = get_object_or_404(Activity, pk=activity_id)
    real_entity = entity.get_real_entity()

    if entity is not real_entity and \
       entity.get_absolute_url() != real_entity.get_absolute_url():
        return redirect(real_entity)

    request.user.has_perm_to_view_or_die(real_entity)
    LastViewedItem(request, real_entity)

    return render(request, 'activities/view_activity.html',
                  {'object': real_entity, 'path': '/activities/activity'},
                 )

@login_required
@permission_required('activities')
def popupview(request, activity_id):
    #TODO: use view_entity instead ? (see below)
    return view_real_entity(request, activity_id, '/activities/activity',
                            'activities/view_activity_popup.html',
                           )

@login_required
@permission_required('activities')
def listview(request, type_id=None):
    kwargs = {}

    if type_id:
        #TODO: change 'add' button too ??
        kwargs['extra_q'] = Q(type=type_id)

    return list_view(request, Activity,
                     extra_dict={'add_url': '/activities/activity/add',
                                 'extra_bt_templates': ('activities/frags/ical_list_view_button.html', )
                                },
                     **kwargs
                    )

@login_required
@permission_required('activities')
def download_ical(request, ids):
    #TODO: is_deleted=False ??
    activities = EntityCredentials.filter(queryset=Activity.objects.filter(pk__in=ids.split(',')),
                                          user=request.user
                                         )
    response = HttpResponse(get_ical(activities), content_type="text/calendar")
    response['Content-Disposition'] = "attachment; filename=Calendar.ics"

    return response

@jsonify
@login_required
def get_types(request, type_id):
    get_object_or_404(ActivityType, pk=type_id)
    return list(ActivitySubType.objects.filter(type=type_id)
                                       .order_by('id')
                                       .values_list('id', 'name')
               )
