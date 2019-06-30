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

from functools import partial
import logging

from django.apps import apps
from django.utils.translation import gettext as _

from creme.creme_core import bricks as core_bricks
from creme.creme_core.core.entity_cell import EntityCellRegularField
from creme.creme_core.models import SearchConfigItem, HeaderFilter, BrickDetailviewLocation
from creme.creme_core.management.commands.creme_populate import BasePopulator

from . import get_graph_model, bricks
from .constants import DEFAULT_HFILTER_GRAPH

logger = logging.getLogger(__name__)


class Populator(BasePopulator):
    dependencies = ['creme_core']

    def populate(self):
        Graph = get_graph_model()

        HeaderFilter.create(
            pk=DEFAULT_HFILTER_GRAPH, name=_('Graph view'), model=Graph,
            cells_desc=[(EntityCellRegularField, {'name': 'name'})],
        )

        SearchConfigItem.create_if_needed(Graph, ['name'])

        # NB: no straightforward way to test that this populate script has not been already run
        if not BrickDetailviewLocation.objects.filter_for_model(Graph).exists():
            create_bdl = partial(BrickDetailviewLocation.objects.create_if_needed, model=Graph)
            LEFT  = BrickDetailviewLocation.LEFT
            RIGHT = BrickDetailviewLocation.RIGHT

            BrickDetailviewLocation.objects.create_for_model_brick(order=5,   zone=LEFT,  model=Graph)
            create_bdl(brick=core_bricks.CustomFieldsBrick,        order=40,  zone=LEFT)
            create_bdl(brick=bricks.RootNodesBrick,                order=60,  zone=LEFT)
            create_bdl(brick=bricks.OrbitalRelationTypesBrick,     order=65,  zone=LEFT)
            create_bdl(brick=core_bricks.PropertiesBrick,          order=450, zone=LEFT)
            create_bdl(brick=core_bricks.RelationsBrick,           order=500, zone=LEFT)
            create_bdl(brick=core_bricks.HistoryBrick,             order=20,  zone=RIGHT)

            if apps.is_installed('creme.assistants'):
                logger.info('Assistants app is installed => we use the assistants blocks on detail view')

                from creme.assistants import bricks as a_bricks

                create_bdl(brick=a_bricks.TodosBrick,        order=100, zone=RIGHT)
                create_bdl(brick=a_bricks.MemosBrick,        order=200, zone=RIGHT)
                create_bdl(brick=a_bricks.AlertsBrick,       order=300, zone=RIGHT)
                create_bdl(brick=a_bricks.UserMessagesBrick, order=400, zone=RIGHT)

            if apps.is_installed('creme.documents'):
                # logger.info('Documents app is installed => we use the documents blocks on detail view')

                from creme.documents.bricks import LinkedDocsBrick

                create_bdl(brick=LinkedDocsBrick, order=600, zone=RIGHT)
