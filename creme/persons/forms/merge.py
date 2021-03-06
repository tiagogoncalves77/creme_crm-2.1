# -*- coding: utf-8 -*-

################################################################################
#    Creme is a free/open-source Customer Relationship Management software
#    Copyright (C) 2009-2019  Hybird
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

from django.utils.translation import gettext as _

from creme.creme_core.forms.merge import MergeEntitiesBaseForm, mergefield_factory
from creme.creme_core.models import FieldsConfig

from creme import persons


Contact = persons.get_contact_model()
Address = persons.get_address_model()

_BILL_PREFIX = 'billaddr_'
_SHIP_PREFIX = 'shipaddr_'


class _PersonMergeForm(MergeEntitiesBaseForm):
    _address_field_names = ()  # Overloaded by get_merge_form_builder()

    def __init__(self, entity1, entity2, *args, **kwargs):
        if isinstance(entity1, Contact):  # TODO: create a ContactMergeForm ?
            if entity2.is_user:
                if entity1.is_user:
                    raise self.CanNotMergeError(_('Can not merge 2 Contacts which represent some users.'))

                entity1, entity2 = entity2, entity1
        else:
            assert isinstance(entity1, persons.get_organisation_model())

            if entity2.is_managed and not entity1.is_managed:
                entity1, entity2 = entity2, entity1

        super().__init__(entity1, entity2, *args, **kwargs)

    def _build_initial_address_dict(self, address, initial, prefix):
        getter = (lambda fname: '') if address is None else \
                 lambda fname: getattr(address, fname)

        for fname in self._address_field_names:
            initial[prefix + fname] = getter(fname)

    def _build_initial_dict(self, entity):
        initial = super()._build_initial_dict(entity)

        build = self._build_initial_address_dict
        build(entity.billing_address,  initial, _BILL_PREFIX)
        build(entity.shipping_address, initial, _SHIP_PREFIX)

        return initial

    def _handle_addresses(self, entity1, entity2, attr_name, cleaned_data, prefix, name):
        entity1_has_changed = False

        address1 = getattr(entity1, attr_name, None)
        address2 = getattr(entity2, attr_name, None)

        address = address1 if address1 is not None else \
                  address2 if address2 is not None else \
                  Address(name=name)

        address_is_empty = True  # We do not use Address.__bool__() because we ignore the address' name.
        for fname in self._address_field_names:
            value = cleaned_data.get(prefix + fname)
            setattr(address, fname, value)

            if value:
                address_is_empty = False

        if not address_is_empty or address.pk is not None:
            address.owner = entity1
            address.save()  # TODO: only if has changed ?

            if address is address1:
                if address2 is not None:
                    address2.delete()
            else:
                setattr(entity1, attr_name, address)
                entity1_has_changed = True

        return entity1_has_changed

    def _post_entity1_update(self, entity1, entity2, cleaned_data):
        super()._post_entity1_update(entity1, entity2, cleaned_data)
        handle_addr = self._handle_addresses

        must_save1 = handle_addr(entity1, entity2, 'billing_address',  cleaned_data, _BILL_PREFIX, _('Billing address'))
        must_save2 = handle_addr(entity1, entity2, 'shipping_address', cleaned_data, _SHIP_PREFIX, _('Shipping address'))

        if must_save1 or must_save2:
            entity1.save()


# TODO: can we build the form once instead of build it each time ??
# TODO: factorise with lv_import.py ?
def get_merge_form_builder(model, base_form_class=_PersonMergeForm):
    address_field_names = [*Address.info_field_names()]
    # TODO: factorise with lv_import.py
    try:
        address_field_names.remove('name')
    except ValueError:
       pass

    attrs = {'_address_field_names': address_field_names}

    get_field = Address._meta.get_field
    fields = [get_field(field_name) for field_name in address_field_names]

    is_hidden = FieldsConfig.get_4_model(model).is_fieldname_hidden

    def add_fields(attr_name, prefix):
        fnames = []

        if not is_hidden(attr_name):
            for field in fields:
                form_fieldname = prefix + field.name
                attrs[form_fieldname] = mergefield_factory(field)
                fnames.append(form_fieldname)

        return fnames

    billing_address_fnames  = add_fields('billing_address', _BILL_PREFIX)
    shipping_address_fnames = add_fields('shipping_address', _SHIP_PREFIX)

    attrs['blocks'] = MergeEntitiesBaseForm.blocks.new(
        ('billing_address',  _('Billing address'),  billing_address_fnames),
        ('shipping_address', _('Shipping address'), shipping_address_fnames),
    )

    return type('PersonMergeForm', (base_form_class,), attrs)
