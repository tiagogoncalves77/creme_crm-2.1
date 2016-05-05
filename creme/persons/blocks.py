# -*- coding: utf-8 -*-

################################################################################
#    Creme is a free/open-source Customer Relationship Management software
#    Copyright (C) 2009-2016  Hybird
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

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

from creme.creme_core.gui.block import Block, SimpleBlock, PaginatedBlock, QuerysetBlock, list4url
from creme.creme_core.models import Relation

from creme.activities import get_activity_model
from creme.activities.constants import (REL_SUB_PART_2_ACTIVITY, REL_SUB_ACTIVITY_SUBJECT,
        REL_SUB_LINKED_2_ACTIVITY, REL_OBJ_PART_2_ACTIVITY)

from . import get_address_model, get_contact_model, get_organisation_model
from .constants import (REL_SUB_MANAGES, REL_OBJ_MANAGES,
        REL_SUB_EMPLOYED_BY, REL_OBJ_EMPLOYED_BY, REL_SUB_CUSTOMER_SUPPLIER,
        REL_SUB_PROSPECT, REL_SUB_INACTIVE)


Address = get_address_model()
Contact = get_contact_model()
Organisation = get_organisation_model()
Activity = get_activity_model()


# class ContactBlock(SimpleBlock):
#     template_name = 'persons/templatetags/block_contact.html'


# class ContactCoordinatesBlock(SimpleBlock):
#     id_           = SimpleBlock.generate_id('persons', 'contact_coordinates')
#     dependencies  = (Contact,)
#     verbose_name  = _(u'Coordinates of a contact')
#     template_name = 'persons/templatetags/block_contact_coordinates.html'
#     target_ctypes = (Contact,)


# class OrganisationBlock(SimpleBlock):
#     template_name = 'persons/templatetags/block_organisation.html'


# class OrgaCoordinatesBlock(SimpleBlock):
#     id_           = SimpleBlock.generate_id('persons', 'orga_coordinates')
#     dependencies  = (Organisation,)
#     verbose_name  = _(u'Coordinates of an organisation')
#     template_name = 'persons/templatetags/block_orga_coordinates.html'
#     target_ctypes = (Organisation,)


class ManagersBlock(QuerysetBlock):
    id_           = QuerysetBlock.generate_id('persons', 'managers')
    dependencies  = (Relation, Contact)
    relation_type_deps = (REL_OBJ_MANAGES, )
    verbose_name  = _(u"Organisation managers")
    template_name = 'persons/templatetags/block_managers.html'
    target_ctypes = (Organisation,)

    def _get_people_qs(self, orga):
        return orga.get_managers()

    def _get_add_title(self):
        return _(u'Create a manager')  # Lazy -> translated only if used

    def detailview_display(self, context):
        orga = context['object']
        is_hidden = context['fields_configs'].get_4_model(Contact).is_fieldname_hidden

        return self._render(self.get_block_template_context(context,
                                self._get_people_qs(orga).select_related('civility'),
                                update_url='/creme_core/blocks/reload/%s/%s/' % (self.id_, orga.pk),
                                rtype_id=self.relation_type_deps[0],
                                ct=ContentType.objects.get_for_model(Contact),
                                add_title=self._get_add_title(),
                                hidden_fields={fname
                                                for fname in ('phone', 'mobile', 'email')
                                                    if is_hidden(fname)
                                              },
                               )
                           )


class EmployeesBlock(ManagersBlock):
    id_           = QuerysetBlock.generate_id('persons', 'employees')
    relation_type_deps = (REL_OBJ_EMPLOYED_BY, )
    verbose_name  = _(u"Organisation employees")
    template_name = 'persons/templatetags/block_employees.html'

    def _get_people_qs(self, orga):
        return orga.get_employees()

    def _get_add_title(self):
        return _(u'Create an employee')  # Lazy -> translated only if used


class NeglectedOrganisationsBlock(PaginatedBlock):
    """Customers/propsects organisations that have no Activity in the future."""
    id_           = PaginatedBlock.generate_id('persons', 'neglected_orgas')
    dependencies  = (Activity,)
    verbose_name  = _(u"Neglected organisations")
    template_name = 'persons/templatetags/block_neglected_orgas.html'
    target_apps   = ('persons',)

    _RTYPE_IDS_CUSTOMERS = (REL_SUB_CUSTOMER_SUPPLIER, REL_SUB_PROSPECT)
    _RTYPE_IDS_ORGA_N_ACT = (REL_SUB_ACTIVITY_SUBJECT, REL_SUB_LINKED_2_ACTIVITY)
    _RTYPE_IDS_EMPLOYEES = (REL_SUB_MANAGES, REL_SUB_EMPLOYED_BY)
    _RTYPE_IDS_CONTACT_N_ACT = (REL_SUB_PART_2_ACTIVITY, REL_SUB_ACTIVITY_SUBJECT, REL_SUB_LINKED_2_ACTIVITY)

    def _get_neglected(self, now):
        user_contacts     = Contact.objects.filter(is_user__isnull=False).values_list('id', flat=True)
        future_activities = list(Activity.objects.filter(start__gte=now,
                                                         relations__type=REL_OBJ_PART_2_ACTIVITY,
                                                         relations__object_entity__in=user_contacts,
                                                        )
                                                 .values_list('id', flat=True)
                                )
        neglected_orgas_qs = Organisation.objects.filter(is_deleted=False,
                                                         relations__type__in=self._RTYPE_IDS_CUSTOMERS,
                                                         relations__object_entity__in=Organisation.get_all_managed_by_creme(),
                                                        ) \
                                                 .exclude(relations__type=REL_SUB_INACTIVE) \
                                                 .distinct()

        if not future_activities:
            return neglected_orgas_qs  # No need to rerieve it & transform into a list (good idea ??)

        neglected_orgas = list(neglected_orgas_qs.exclude(relations__object_entity__in=future_activities,
                                                          relations__type__in=self._RTYPE_IDS_ORGA_N_ACT,
                                                         )
                              )

        if neglected_orgas:
            linked_people_map = dict(Relation.objects.filter(type__in=self._RTYPE_IDS_EMPLOYEES,
                                                             object_entity__in=[o.id for o in neglected_orgas],
                                                            )
                                                     .values_list('subject_entity_id', 'object_entity_id')
                                    )
            activity_links = Relation.objects.filter(type__in=self._RTYPE_IDS_CONTACT_N_ACT,
                                                     subject_entity__in=linked_people_map.keys(),
                                                     object_entity__in=future_activities,
                                                    )

            neglected_map = {orga.id: True for orga in neglected_orgas}  # 'True' means 'neglected'
            for rel in activity_links:
                neglected_map[linked_people_map[rel.subject_entity_id]] = False

            neglected_orgas = [orga for orga in neglected_orgas if neglected_map[orga.id]]

        return neglected_orgas

    def portal_display(self, context, ct_ids):
        if not context['user'].has_perm('persons'):
            raise PermissionDenied('Error: you are not allowed to view this block: %s' % self.id_)

        return self._render(self.get_block_template_context(
                                context,
                                self._get_neglected(context['today']),
                                update_url='/creme_core/blocks/reload/portal/%s/%s/' % (
                                                    self.id_, list4url(ct_ids),
                                                ),
                               )
                           )


# TODO: factorise (see CSV import) ? (exclue param in info_field_names())
def _get_address_field_names():
    field_names = list(Address.info_field_names())

    try:
       field_names.remove('name')
    except ValueError:
       pass

    return field_names


class AddressBlock(Block):
    id_           = Block.generate_id('persons', 'address')
    dependencies  = (Address,)
    verbose_name  = _(u'Address')
    template_name = 'persons/templatetags/block_address.html'
    target_ctypes = (Contact, Organisation)

    def detailview_display(self, context):
        person = context['object']
        model = person.__class__
        is_hidden = context['fields_configs'].get_4_model(model)\
                                             .is_field_hidden

        def prepare_address(attr_name):
            display_button = display_content = False

            try:
                addr = getattr(person, attr_name)
            except AttributeError:
                addr = Address()
            else:
                if is_hidden(model._meta.get_field(attr_name)):
                    if addr is None:
                        addr = Address()
                elif addr is None:
                    addr = Address()
                    display_button = True
                else:
                    display_content = True

            addr.display_button  = display_button
            addr.display_content = display_content

            addr.owner = person  # NB: avoids a query (per address) for credentials.

            return addr

        b_address = prepare_address('billing_address')
        s_address = prepare_address('shipping_address')

        colspan = 0
        if b_address.display_content: colspan += 3
        if s_address.display_content: colspan += 3
        if not colspan: colspan = 1

        return self._render(self.get_block_template_context(
                                context,
                                update_url='/creme_core/blocks/reload/%s/%s/' % (
                                                self.id_, person.pk,
                                            ),
                                b_address=b_address,
                                s_address=s_address,
                                field_names=_get_address_field_names(),  # TODO: cache in context ??
                                address_model=Address,  # For fields' verbose name
                                colspan=colspan,
                               )
                           )


class OtherAddressBlock(QuerysetBlock):
    id_           = QuerysetBlock.generate_id('persons', 'other_address')
    dependencies  = (Address,)
    verbose_name  = _(u'Other Address')
    template_name = 'persons/templatetags/block_other_address.html'
    target_ctypes = (Contact, Organisation)
    page_size     = 1

    _ADDRESS_CT_ID = ContentType.objects.get_for_model(Address).id

    def detailview_display(self, context):
        person = context['object']

        return self._render(self.get_block_template_context(
                                context,
                                person.other_addresses,
                                update_url='/creme_core/blocks/reload/%s/%s/' % (
                                                self.id_, person.pk,
                                            ),
                                field_names=_get_address_field_names(),
                                ct_id=self._ADDRESS_CT_ID,
                               )
                           )


# contact_coord_block   = ContactCoordinatesBlock()
# orga_coord_block      = OrgaCoordinatesBlock()
address_block         = AddressBlock()
other_address_block   = OtherAddressBlock()
managers_block        = ManagersBlock()
employees_block       = EmployeesBlock()
neglected_orgas_block = NeglectedOrganisationsBlock()

block_list = (
#        contact_coord_block,
#        orga_coord_block,
        address_block,
        other_address_block,
        managers_block,
        employees_block,
        neglected_orgas_block,
    )
