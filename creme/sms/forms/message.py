# -*- coding: utf-8 -*-

################################################################################
#    Creme is a free/open-source Customer Relationship Management software
#    Copyright (C) 2009-2010  Hybird
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

from django.utils.translation import ugettext_lazy as _

from creme_core.forms.base import CremeModelForm
from creme_core.forms.fields import CremeEntityField

from sms.models.message import Sending, Message, MESSAGE_STATUS_NOTSENT
from sms.models.template import MessageTemplate

class SendingCreateForm(CremeModelForm):
    class Meta:
        model   = Sending
        exclude = ('campaign', 'date', 'content')

    template     = CremeEntityField(label=_(u'Patron de message'), model=MessageTemplate)

    def __init__(self, campaign, *args, **kwargs):
            super(SendingCreateForm, self).__init__(*args, **kwargs)
            self.campaign = campaign

    def save(self):
        instance = self.instance
        instance.campaign = self.campaign
        instance.date = datetime.now()
        super(SendingCreateForm, self).save()

        template = instance.template
        instance.content = (template.subject + ' : ' + template.body) if template else ''
        instance.save()

        for phone in instance.campaign.all_recipients():
            Message.objects.create(phone=phone,
                                   status=MESSAGE_STATUS_NOTSENT,
                                   sending=instance)

        Message.send(instance)
