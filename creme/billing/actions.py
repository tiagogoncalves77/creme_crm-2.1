# -*- coding: utf-8 -*-

################################################################################
#    Creme is a free/open-source Customer Relationship Management software
#    Copyright (C) 2018  Hybird
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

from django.urls.base import reverse
from django.utils.translation import ugettext_lazy as _

from creme import billing
from creme.creme_core.gui import actions


Invoice = billing.get_invoice_model()
Quote   = billing.get_quote_model()


class ExportActionEntry(actions.ActionEntry):
    action = 'redirect'

    label = _('Download')
    icon = 'download'
    help_text = _('Download as PDF')

    @property
    def url(self):
        return reverse('billing__export', args=(self.instance.id,))

    @property
    def is_enabled(self):
        return self.user.has_perm_to_view(self.instance)


class ExportInvoiceActionEntry(ExportActionEntry):
    action_id = 'billing-export_invoice'
    model = Invoice


class ExportQuoteActionEntry(ExportActionEntry):
    action_id = 'billing-export_quote'
    model = Quote
