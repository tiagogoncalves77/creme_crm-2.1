# -*- coding: utf-8 -*-

# from django.utils.translation import ugettext_lazy as _

# from creme.creme_core.auth.decorators import login_required, permission_required
from creme.creme_core.views import generic

from ..tests import fake_models, fake_forms


# @login_required
# @permission_required('creme_core')
# def document_listview(request):
#     return generic.list_view(request, fake_models.FakeDocument)
class FakeDocumentsList(generic.EntitiesList):
    model = fake_models.FakeDocument


class FakeImageDetail(generic.EntityDetail):
    model = fake_models.FakeImage
    pk_url_kwarg = 'image_id'


# @login_required
# @permission_required('creme_core')
# def image_listview(request):
#     return generic.list_view(request, fake_models.FakeImage)
class FakeImagesList(generic.EntitiesList):
    model = fake_models.FakeImage


class FakeContactCreation(generic.EntityCreation):
    model = fake_models.FakeContact
    form_class = fake_forms.FakeContactForm


class FakeContactEdition(generic.EntityEdition):
    model = fake_models.FakeContact
    form_class = fake_forms.FakeContactForm
    pk_url_kwarg = 'contact_id'


class FakeContactDetail(generic.EntityDetail):
    model = fake_models.FakeContact
    # template_name = 'creme_core/tests/view-fake-contact.html'  TODO ?
    pk_url_kwarg = 'contact_id'


# @login_required
# @permission_required('creme_core')
# def contact_listview(request):
#     return generic.list_view(request, fake_models.FakeContact)
class FakeContactsList(generic.EntitiesList):
    model = fake_models.FakeContact


# @login_required
# @permission_required(('creme_core', 'creme_core.add_fakeorganisation'))
# def organisation_add(request):
#     return generic.add_entity(request, fake_forms.FakeOrganisationForm)
class FakeOrganisationCreation(generic.EntityCreation):
    model = fake_models.FakeOrganisation
    form_class = fake_forms.FakeOrganisationForm


# @login_required
# @permission_required('creme_core')
# def organisation_edit(request, orga_id):
#     return generic.edit_entity(request, orga_id, fake_models.FakeOrganisation,
#                                fake_forms.FakeOrganisationForm,
#                               )
class FakeOrganisationEdition(generic.EntityEdition):
    model = fake_models.FakeOrganisation
    form_class = fake_forms.FakeOrganisationForm
    pk_url_kwarg = 'orga_id'


# @login_required
# @permission_required('creme_core')
# def organisation_detailview(request, orga_id):
#     # NB: keep legacy for tests
#     return generic.view_entity(request, orga_id, fake_models.FakeOrganisation)
class FakeOrganisationDetail(generic.EntityDetail):
    model = fake_models.FakeOrganisation
    # template_name = 'creme_core/tests/view-fake-organisation.html'  TODO ?
    pk_url_kwarg = 'orga_id'


# @login_required
# @permission_required('creme_core')
# def organisation_listview(request):
#     return generic.list_view(request, fake_models.FakeOrganisation)
class FakeOrganisationsList(generic.EntitiesList):
    model = fake_models.FakeOrganisation

# @login_required
# @permission_required('creme_core')
# def address_add(request, entity_id):
#     return generic.add_to_entity(request, entity_id, fake_forms.FakeAddressForm,
#                                  'Adding address to <%s>',
#                                  submit_label=_('Save the address'),
#                                 )


class FakeAddressCreation(generic.AddingInstanceToEntityPopup):
    model = fake_models.FakeAddress
    form_class = fake_forms.FakeAddressForm
    title = 'Adding address to <{entity}>'


# @login_required
# @permission_required('creme_core')
# def address_edit(request, address_id):
#     return generic.edit_related_to_entity(request, address_id,
#                                           fake_models.FakeAddress,
#                                           fake_forms.FakeAddressForm,
#                                           'Address for <%s>',
#                                          )


class FakeAddressEdition(generic.RelatedToEntityEditionPopup):
    model = fake_models.FakeAddress
    pk_url_kwarg = 'address_id'
    form_class = fake_forms.FakeAddressForm
    title = 'Address for <{entity}>'


# @login_required
# @permission_required('creme_core')
# def activity_listview(request):
#     return generic.list_view(request, fake_models.FakeActivity)
class FakeActivitiesList(generic.EntitiesList):
    model = fake_models.FakeActivity


# @login_required
# @permission_required('creme_core')
# def campaign_listview(request):
#     return generic.list_view(request, fake_models.FakeEmailCampaign)
class FakeEmailCampaignsList(generic.EntitiesList):
    model = fake_models.FakeEmailCampaign


class FakeInvoiceDetail(generic.EntityDetail):
    model = fake_models.FakeInvoice
    pk_url_kwarg = 'invoice_id'


# @login_required
# @permission_required('creme_core')
# def invoice_listview(request):
#     return generic.list_view(request, fake_models.FakeInvoice)
class FakeInvoicesList(generic.EntitiesList):
    model = fake_models.FakeInvoice


# @login_required
# @permission_required('creme_core')
# def invoice_lines_listview(request):
#     return generic.list_view(request, fake_models.FakeInvoiceLine, show_actions=False)
class FakeInvoiceLinesList(generic.EntitiesList):
    model = fake_models.FakeInvoiceLine

    def get_show_actions(self):
        return False


# @login_required
# @permission_required('creme_core')
# def mailing_lists_listview(request):
#     return generic.list_view(request, fake_models.FakeMailingList)
class FakeMailingListsList(generic.EntitiesList):
    model = fake_models.FakeMailingList
