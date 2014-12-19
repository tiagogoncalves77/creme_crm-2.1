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

from django.utils.translation import ugettext

from creme.creme_core.core.setting_key import SettingKey

from .constants import DEFAULT_SEPARATING_NEIGHBOURS

NEIGHBOURHOOD_DISTANCE = SettingKey(id="geolocation-neighbourhood_distance",
                                    description=ugettext(u"Maximum distance to find neighbours in meters, default %(default)s m.") % {'default': DEFAULT_SEPARATING_NEIGHBOURS},
                                    app_label='geolocation', type=SettingKey.INT
                                   )