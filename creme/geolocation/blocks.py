# -*- coding: utf-8 -*-

################################################################################
#    Creme is a free/open-source Customer Relationship Management software
#    Copyright (C) 2014  Hybird
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

from json import dumps as encode_json

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext, ugettext_lazy as _

from creme.creme_core.models import EntityFilter
from creme.creme_core.gui.block import Block

from creme.persons.models import Contact, Organisation, Address

from .constants import DEFAULT_SEPARATING_NEIGHBOURS
from .setting_keys import NEIGHBOURHOOD_DISTANCE
from .utils import address_as_dict, get_setting

from .models import GeoAddress


class _MapBlock(Block):
    dependencies  = (Address,) 

    def get_efilters(self, model):
        return EntityFilter.objects.filter(entity_type=ContentType.objects.get_for_model(model))

    def get_filter_choices(self, *models):
        choices = []

        for model in models:
            title = ugettext(model._meta.verbose_name_plural)
            model_choices = [(efilter.id, u'%s - %s' % (title, efilter.name)) for efilter in self.get_efilters(model)]

            if model_choices:
                choices.append((title, model_choices))

        return choices

    def get_addresses(self, entity):
        return Address.objects.filter(object_id=entity.id).select_related('geoaddress')


class PersonsMapsBlock(_MapBlock):
    id_           = Block.generate_id('persons', 'geolocation')
    verbose_name  = _(u'Maps')
    template_name = 'geolocation/templatetags/block_persons_google_map.html'
    target_ctypes = (Contact, Organisation)

    def detailview_display(self, context):
        entity = context['object']
        addresses = self.get_addresses(entity)
        return self._render(self.get_block_template_context(context,
                                                            update_url='/creme_core/blocks/reload/%s/%s/' % (self.id_, entity.pk),
                                                            entity_addresses=addresses,
                                                            geoaddresses=encode_json([address_as_dict(address) for address in addresses]),
                                                           )
                           )


class PersonsFiltersMapsBlock(_MapBlock):
    id_           = Block.generate_id('persons_filters', 'geolocation')
    verbose_name  = _(u'Maps By Filter')
    template_name = 'geolocation/templatetags/block_persons_filters_google_map.html'

    def home_display(self, context):
        address_filters = self.get_filter_choices(Contact, Organisation)

        btc = self.get_block_template_context(context,
                                              update_url='/creme_core/blocks/reload/home/%s/' % self.id_,
                                              address_filters=address_filters,
                                             )
        return self._render(btc)


class WhoisAroundMapsBlock(_MapBlock):
    dependencies  = (Address, GeoAddress,)
    id_           = Block.generate_id('whoisarround', 'geolocation')
    verbose_name  = _(u'Around this address')
    template_name = 'geolocation/templatetags/block_persons_who_is_arround_map.html'
    target_ctypes = (Contact, Organisation)

    # Specific use case
    # Add a new ungeolocatable
    # the person bloc will show an error message
    # this bloc will show an empty select
    # edit this address with a geolocatable address
    # the person block is reloaded and the address is asynchronously geocoded
    # This block is reloaded in the same time and the address has no info yet.

    def detailview_display(self, context):
        entity = context['object']
        addresses = self.get_addresses(entity)
        address_filters = self.get_filter_choices(Contact, Organisation)

        btc = self.get_block_template_context(
                    context,
                    update_url='/creme_core/blocks/reload/%s/%s/' % (self.id_, entity.pk),
                    address_filters=address_filters,
                    radius=get_setting(NEIGHBOURHOOD_DISTANCE, DEFAULT_SEPARATING_NEIGHBOURS),
                    ref_addresses=[address for address in addresses if address.geoaddress.latitude],
                   )
        return self._render(btc)


persons_maps_block        = PersonsMapsBlock()
persons_filter_maps_block = PersonsFiltersMapsBlock()
who_is_around_maps_block  = WhoisAroundMapsBlock()

block_list = (
    persons_maps_block,
    persons_filter_maps_block,
    who_is_around_maps_block,
)