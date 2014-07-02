# -*- coding: utf-8 -*-

try:
    from datetime import timedelta
    from functools import partial

    from django.conf import settings
    from django.contrib.contenttypes.models import ContentType
    from django.utils.formats import date_format
    from django.utils.timezone import now

    from creme.creme_core.tests.base import CremeTestCase, skipIfNotInstalled

    if 'creme.tickets' in settings.INSTALLED_APPS:
        from creme.tickets.models import Ticket, TicketTemplate, Status, Priority, Criticity
        tickets_installed = True
    else:
        tickets_installed = False

    from ..management.commands.recurrents_gendocs import Command as GenDocsCommand
    from ..models import Periodicity, RecurrentGenerator
except Exception as e:
    print('Error in <%s>: %s' % (__name__, e))


__all__ = ('RecurrentsTicketsTestCase',)


class RecurrentsTicketsTestCase(CremeTestCase):
    @classmethod
    def setUpClass(cls):
        CremeTestCase.setUpClass()
        apps = ['creme_config', 'recurrents']

        if tickets_installed:
            apps.append('tickets')

        cls.populate(*apps)

        cls.ct = ContentType.objects.get_for_model(Ticket)

    def setUp(self):
        self.login()

    def test_portal(self):
        self.assertGET200('/recurrents/')

    def _create_ticket_template(self, title='Support ticket'):
        return TicketTemplate.objects.create(user=self.user,
                                             title=title,
                                             status=Status.objects.all()[0],
                                             priority=Priority.objects.all()[0],
                                             criticity=Criticity.objects.all()[0],
                                            )

    def _get_weekly(self):
        return Periodicity.objects.get_or_create(value_in_days=7,
                                                 defaults={'name': 'Weekly'}
                                                )[0]

    @skipIfNotInstalled('creme.tickets')
    def test_createview(self):
        user = self.user
        url = '/recurrents/generator/add'
        self.assertGET200(url)

        name = 'Recurrent tickets'
        periodicity = Periodicity.objects.all()[0]
        step_0_data = {'wizard_step':        0,
                       '0-user':             user.id,
                       '0-name':             name,
                       '0-ct':               self.ct.id,
                       '0-first_generation': '11-06-2014 09:00',
                       '0-periodicity':      periodicity.id,
                      }
        response = self.client.post(url, data=step_0_data)
        self.assertNoFormError(response)

        with self.assertNoException():
            response.context['form']
            previous_fields = response.context['previous_fields']

        self.assertIn('<input type="hidden" name="0-user" value="%s" id="id_0-user" />' % user.id,
                      previous_fields
                     )
        self.assertIn(u'<input type="hidden" name="0-name" value="%s" id="id_0-name" />' % name,
                      previous_fields
                     )

        hash_input = '<input type="hidden" name="hash_0" value="'
        hash_start = previous_fields.find(hash_input)
        hash_start += len(hash_input)
        self.assertNotEqual(-1, hash_start)
        hash_end = previous_fields.find('"', hash_start)
        self.assertNotEqual(-1, hash_end)

        title     = 'Support ticket'
        desc      = "blablabla"
        status    = Status.objects.all()[0]
        priority  = Priority.objects.all()[0]
        criticity = Criticity.objects.all()[0]
        response = self.client.post(url, follow=True,
                                    data=dict(step_0_data,
                                              **{'wizard_step': 1,
                                                 'hash_0':      previous_fields[hash_start:hash_end],

                                                 '1-user':        user.id,
                                                 '1-title':       title,
                                                 '1-description': desc,
                                                 '1-status':      status.id,
                                                 '1-priority':    priority.id,
                                                 '1-criticity':   criticity.id,
                                                }
                                             ),
                                   )
        self.assertNoFormError(response)

        gen = self.get_object_or_fail(RecurrentGenerator, name=name)
        tpl = self.get_object_or_fail(TicketTemplate, title=title)

        self.assertEqual(user,        gen.user)
        self.assertEqual(name,        gen.name)
        self.assertEqual(self.ct,     gen.ct)
        self.assertEqual(periodicity, gen.periodicity)
        self.assertEqual(self.create_datetime(year=2014, month=6, day=11, hour=9),
                         gen.first_generation
                        )
        self.assertEqual(gen.last_generation, gen.first_generation)
        self.assertEqual(tpl, gen.template.get_real_entity())
        self.assertTrue(gen.is_working)

        self.assertEqual(user,      tpl.user)
        self.assertEqual(title,     tpl.title)
        self.assertEqual(desc,      tpl.description)
        self.assertEqual(status,    tpl.status)
        self.assertEqual(priority,  tpl.priority)
        self.assertEqual(criticity, tpl.criticity)
        self.assertFalse(tpl.solution)

    @skipIfNotInstalled('creme.tickets')
    def test_editview(self):
        user = self.user

        old_per, new_per = Periodicity.objects.all()[:2]

        tpl1 = self._create_ticket_template(title='TicketTemplate #1')
        tpl2 = self._create_ticket_template(title='TicketTemplate #2')

        gen = RecurrentGenerator.objects.create(name='Gen1', user=user,
                                                periodicity=old_per,
                                                ct=self.ct, template=tpl1,
                                               )

        url = '/recurrents/generator/edit/%s' % gen.id
        self.assertGET200(url)

        name = gen.name.upper()
        response = self.client.post(url, follow=True,
                                    data={'user':             user.id,
                                          'name':             name,
                                          'first_generation': '12-06-2014 10:00',
                                          'periodicity':      new_per.id,

                                          # should not be used
                                          'ct': ContentType.objects.get_for_model(Periodicity).id,
                                          'template': tpl2.id,
                                         }
                                   )
        self.assertNoFormError(response)
        self.assertRedirects(response, gen.get_absolute_url())

        gen = self.refresh(gen)
        self.assertEqual(name, gen.name)
        self.assertEqual(self.create_datetime(year=2014, month=6, day=12, hour=10),
                         gen.first_generation
                        )
        self.assertEqual(self.ct, gen.ct)
        self.assertEqual(tpl1, gen.template.get_real_entity())

    @skipIfNotInstalled('creme.tickets')
    def test_listview(self):
        tpl = self._create_ticket_template()
        periodicity = Periodicity.objects.all()[0]
        create_gen = partial(RecurrentGenerator.objects.create, user=self.user,
                             periodicity=periodicity, ct=self.ct,
                             template=tpl,
                            )
        gen1 = create_gen(name='Gen1')
        gen2 = create_gen(name='Gen2') 

        response = self.assertGET200('/recurrents/generators')

        with self.assertNoException():
            gens_page = response.context['entities']

        self.assertEqual(2, gens_page.paginator.count)
        self.assertEqual({gen1, gen2}, set(gens_page.object_list))

    @skipIfNotInstalled('creme.tickets')
    def test_command01(self):
        "first_generation == last_generation + in te past"
        self.assertFalse(Ticket.objects.all())

        tpl = self._create_ticket_template()
        now_value = now()
        start = now_value - timedelta(days=5)
        gen = RecurrentGenerator.objects.create(name='Gen1', user=self.user,
                                                periodicity=self._get_weekly(),
                                                ct=self.ct, template=tpl,
                                                first_generation=start,
                                                last_generation=start,
                                               )
        
        GenDocsCommand().handle(verbosity=0)

        new_tickets = Ticket.objects.all()
        self.assertEqual(1, len(new_tickets))

        ticket = new_tickets[0]
        self.assertEqual(u'%s %s #1' % (tpl.title, date_format(now_value.date(), 'DATE_FORMAT')),
                         ticket.title
                        )

    @skipIfNotInstalled('creme.tickets')
    def test_command02(self):
        "last_generation is not far enough"
        tpl = self._create_ticket_template()
        now_value = now()
        gen = RecurrentGenerator.objects.create(name='Gen1', user=self.user,
                                                periodicity=self._get_weekly(),
                                                ct=self.ct, template=tpl,
                                                first_generation=now_value - timedelta(days=13),
                                                last_generation=now_value - timedelta(days=6),
                                               )

        GenDocsCommand().handle(verbosity=0)
        self.assertFalse(Ticket.objects.all())

    @skipIfNotInstalled('creme.tickets')
    def test_command03(self):
        "last_generation is far enough"
        tpl = self._create_ticket_template()
        now_value = now()
        gen = RecurrentGenerator.objects.create(name='Gen1', user=self.user,
                                                periodicity=self._get_weekly(),
                                                ct=self.ct, template=tpl,
                                                first_generation=now_value - timedelta(days=15),
                                                last_generation=now_value - timedelta(days=7),
                                               )
        
        GenDocsCommand().handle(verbosity=0)
        self.assertEqual(1, Ticket.objects.count())