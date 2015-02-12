# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
# pylint: disable=maybe-no-member, too-many-public-methods, invalid-name

from datetime import datetime, date, timedelta
import os.path
import unittest
from unittest.mock import patch

from .main import app, db, mail
from . import main, utils
from .fixtures import fill_db, allow_ordering
from .mocks import (
    MOCK_ADMIN,
    MOCK_DATA_TOMAS,
    MOCK_DATA_KOZIOLEK,
    MOCK_WWW_TOMAS,
    MOCK_WWW_KOZIOLEK,
)
from .models import Order, Food, MailText, User
from .webcrawler import get_dania_dnia_from_pod_koziolek, get_week_from_tomas
from .utils import make_datetime


def setUp():
    """
    Main setup.
    """
    test_config = os.path.join(
        os.path.dirname(__file__),
        '..', '..', 'parts', 'etc', 'test.cfg',
    )
    app.config.from_pyfile(test_config)
    main.init()


class LunchBackendViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        self.client = main.app.test_client()
        db.create_all()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        db.session.remove()
        db.drop_all()

    def test_mainpage_view(self):
        """
        Test main page view.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_info_view(self):
        """
        Test info page view.
        """
        fill_db()
        resp = self.client.get('/info')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("CATERING - menu na co dzi" in resp.data.__str__())
        mailtxt = MailText.query.first()
        mailtxt.info_page_text = "To jest nowa firma \n ze strna\n www.wp.pl"
        db.session.commit()
        resp = self.client.get('/info')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("www.wp.pl" in resp.data.__str__())

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_my_orders_view(self):
        """
        Test my orders page view.
        """
        resp = self.client.get('/my_orders')
        self.assertEqual(resp.status_code, 200)

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_overview_view(self):
        """
        Test overview page.
        """
        resp = self.client.get('/overview')
        self.assertEqual(resp.status_code, 200)

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_create_order_view(self):
        """
        Test create order page.
        """
        allow_ordering()
        resp = self.client.get('/order')
        self.assertEqual(resp.status_code, 200)

        data = {
            'cost': '12',
            'company': 'Pod Koziołkiem',
            'description': 'dobre_jedzonko',
            'send_me_a_copy': 'false',
            'arrival_time': '12:00',
        }
        resp = self.client.post('/order', data=data)
        order_db = Order.query.first()
        self.assertTrue(resp.status_code == 302)
        self.assertEqual(order_db.cost, 12)
        self.assertEqual(order_db.company, 'Pod Koziołkiem')
        self.assertEqual(order_db.description, 'dobre_jedzonko')
        self.assertAlmostEqual(
            order_db.date,
            datetime.now(),
            delta=timedelta(seconds=1),
        )
        self.assertEqual(order_db.arrival_time, '12:00')

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_create_order_with_email(self):
        """
        Test create order with send me an email.
        """
        allow_ordering()
        with mail.record_messages() as outbox:
            data = {
                'cost': '13',
                'company': 'Pod Koziołkiem',
                'description': 'To jest TESTow zamowienie dla emaila',
                'send_me_a_copy': 'true',
                'date': '2015-01-02',
                'arrival_time': '13:00',
            }
            resp = self.client.post('/order', data=data)
            self.assertTrue(resp.status_code == 302)
            self.assertEqual(len(outbox), 1)
            msg = outbox[0]
            self.assertTrue(msg.subject.startswith('Lunch order'))
            self.assertIn('To jest TESTow zamowienie dla emaila', msg.body)
            self.assertIn('Pod Koziołkiem', msg.body)
            self.assertIn('13.0 PLN', msg.body)
            self.assertIn('at 13:00', msg.body)
            self.assertEqual(msg.recipients, ['mock@mock.com'])

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_add_food_view(self):
        """
        Test add food page.
        """
        resp = self.client.get('/add_food')
        self.assertEqual(resp.status_code, 200)
        data = {
            'cost': '333',
            'description': 'dobre_jedzonko',
            'date_available_to': '2015-01-01',
            'company': 'Pod Koziołkiem',
            'date_available_from': '2015-01-01',
            'o_type': 'daniednia',
            'add_meal': 'add',
        }
        resp_2 = self.client.post('/add_food', data=data,)
        food_db = Food.query.first()
        self.assertEqual(resp_2.status_code, 302)
        self.assertEqual(food_db.cost, 333)
        self.assertEqual(food_db.description, 'dobre_jedzonko')
        self.assertEqual(food_db.date_available_to, datetime(2015, 1, 1, 0, 0))
        self.assertEqual(food_db.company, 'Pod Koziołkiem')
        self.assertEqual(food_db.o_type, 'daniednia')
        self.assertEqual(
            food_db.date_available_from,
            datetime(2015, 1, 1, 0, 0)
        )

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_add_food__bulk_view(self):
        """
        Test bulk add food page.
        """
        data = {
            'cost': '333',
            'description': 'dobre_jedzonko\r\nciekawe_jedzonko\r\npies',
            'date_available_to': '2015-01-01',
            'company': 'Pod Koziołkiem',
            'date_available_from': '2015-01-01',
            'o_type': 'daniednia',
            'add_meal': 'bulk',
        }
        resp = self.client.post('/add_food', data=data,)
        food_db = Food.query.get(1)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(food_db.cost, 333)
        self.assertEqual(food_db.description, 'dobre_jedzonko')
        self.assertEqual(food_db.date_available_to, datetime(2015, 1, 1, 0, 0))
        self.assertEqual(food_db.company, 'Pod Koziołkiem')
        self.assertEqual(food_db.o_type, 'daniednia')
        self.assertEqual(
            food_db.date_available_from,
            datetime(2015, 1, 1, 0, 0)
        )
        food_db = Food.query.get(2)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(food_db.cost, 333)
        self.assertEqual(food_db.description, 'ciekawe_jedzonko')
        self.assertEqual(food_db.date_available_to, datetime(2015, 1, 1, 0, 0))
        self.assertEqual(food_db.company, 'Pod Koziołkiem')
        self.assertEqual(food_db.o_type, 'daniednia')
        self.assertEqual(
            food_db.date_available_from,
            datetime(2015, 1, 1, 0, 0)
        )
        food_db = Food.query.get(3)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(food_db.cost, 333)
        self.assertEqual(food_db.description, 'pies')
        self.assertEqual(food_db.date_available_to, datetime(2015, 1, 1, 0, 0))
        self.assertEqual(food_db.company, 'Pod Koziołkiem')
        self.assertEqual(food_db.o_type, 'daniednia')
        self.assertEqual(
            food_db.date_available_from,
            datetime(2015, 1, 1, 0, 0)
        )

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_day_summary_view(self):
        """
        Test day summary page.
        """
        fill_db()
        resp = self.client.get('/day_summary')
        self.assertIn('Maly Gruby Nalesnik', str(resp.data))
        self.assertIn('Duzy Gruby Nalesnik', str(resp.data))
        db.session.close()

    def test_order_list_view(self):
        """
        Test order list page.
        """
        resp = self.client.get('/order_list')
        self.assertEqual(resp.status_code, 200)
        fill_db()
        data = {'year': '2015', 'user': '1'}
        resp = self.client.post('/order_list', data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, 'http://localhost/order_list/1/2015')
        data = {'year': '2015', 'month': '1', 'user': '1'}
        resp = self.client.post('/order_list', data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp.location,
            'http://localhost/order_list/1/2015/1'
        )

    def test_order_list_view_month(self):
        """
        Test order list month page.
        """
        fill_db()
        resp = self.client.get('/order_list/1/2015/1')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Duzy Gruby Nalesnik', str(resp.data))
        self.assertIn('test_user', str(resp.data))
        self.assertIn('Tomas', str(resp.data))
        self.assertIn('2015-01-05', str(resp.data))

    def test_order_list_view_year(self):
        """
        Test order list year page.
        """
        fill_db()
        resp = self.client.get('/order_list/1/2015/1')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('January', str(resp.data))
        self.assertIn('test_user', str(resp.data))
        self.assertIn('Tomas', str(resp.data))
        self.assertIn('123', str(resp.data))

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_edit_order_view(self):
        """
        Test edit order page.
        """
        fill_db()
        resp = self.client.get('/order_edit/1/')
        self.assertEqual(resp.status_code, 200)
        data = {
            'cost': '12',
            'company': 'Pod Koziołkiem',
            'description': 'dobre_jedzonko',
            'send_me_a_copy': 'false',
            'date': '2015-01-01',
            'arrival_time': '12:00',
            'date': '2015-01-01',
        }
        resp = self.client.post('/order_edit/1/', data=data)
        order_db = Order.query.first()
        self.assertTrue(resp.status_code == 302)
        self.assertEqual(order_db.cost, 12)
        self.assertEqual(order_db.company, 'Pod Koziołkiem')
        self.assertEqual(order_db.description, 'dobre_jedzonko')
        self.assertEqual(order_db.date, datetime(2015, 1, 1, 0, 0))
        self.assertEqual(order_db.arrival_time, '12:00')
        self.assertEqual(order_db.date, datetime(2015, 1, 1))

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_delete_order(self):
        """
        Test delete order.
        """
        fill_db()
        resp = self.client.post('/delete_order/1')
        self.assertEqual(resp.status_code, 302)
        order = Order.query.get(1)
        self.assertTrue(order is None)

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_company_summary_view(self):
        """
        Test company summary page.
        """
        resp = self.client.get('/company_summary')
        self.assertEqual(resp.status_code, 200)
        data = {'year': '2015', 'month': '1'}
        resp = self.client.post('/company_summary', data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp.location,
            'http://localhost/company_summary/2015/1',
        )
        resp = self.client.get('/company_summary/2015/1')
        self.assertEqual(resp.status_code, 200)

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_company_summary_month_view(self):
        """
        Test company summary month page.
        """
        fill_db()
        resp = self.client.get('/company_summary/2015/1')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('123', str(resp.data))
        resp = self.client.get('/company_summary/2015/2')
        self.assertIn('489', str(resp.data))
        db.session.close()

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_finance_view(self):
        """
        Test finance page.
        """
        fill_db()
        # all users test
        resp = self.client.get('/finance/2015/2/0')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('test_user', str(resp.data))
        self.assertIn('test@user.pl', str(resp.data))
        self.assertIn('checked="checked"', str(resp.data))
        self.assertIn('x@x.pl', str(resp.data))

        # paid user test
        resp = self.client.get('/finance/2015/2/1')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('test_user', str(resp.data))
        self.assertIn('checked="checked"', str(resp.data))

        # unpaid user test
        resp = self.client.get('/finance/2015/2/2')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('test@user.pl', str(resp.data))
        self.assertIn('x@x.pl', str(resp.data))
        self.assertNotIn('checked=checked', str(resp.data))

        # unpaid user changed to paid test
        data = {
            'did_user_pay_test@user.pl': 'on',
        }
        resp = self.client.post('/finance/2015/2/2', data=data)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/finance/2015/2/2')
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('test@user.pl', str(resp.data))
        resp = self.client.get('/finance/2015/2/1')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('test@user.pl', str(resp.data))
        db.session.close()

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_finance_mail_text_view(self):
        """
        Test finance emial text page.
        """
        fill_db()
        resp = self.client.get('/finance_mail_text')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('daili1', str(resp.data))
        self.assertIn('monthly2', str(resp.data))
        self.assertIn('reminder3', str(resp.data))
        self.assertIn('slacker4', str(resp.data))
        data = {
            'daily_reminder': 'Nowy Daily Reminder',
            'monthly_pay_summary': 'Ciekawszy Montlhy Reminder',
            'pay_reminder': 'Fajniejszy Reminder',
            'pay_slacker_reminder': 'Leniwy przypominacz',
            'info_page_text': 'Nowa strona Tomasa www.wp.pl',
            'daily_reminder_subject': 'STX Lunch nowy temat',
            'blocked_user_text': 'You are banned',
            'ordering_is_blocked_text': 'Ordering is Blocked',
        }
        resp = self.client.post('/finance_mail_text', data=data)
        self.assertEqual(resp.status_code, 302)
        msg_text_db = MailText.query.get(1)
        self.assertEqual(
            msg_text_db.daily_reminder,
            'Nowy Daily Reminder',
        )
        self.assertEqual(
            msg_text_db.monthly_pay_summary,
            'Ciekawszy Montlhy Reminder',
        )
        self.assertEqual(
            msg_text_db.pay_reminder,
            'Fajniejszy Reminder',
        )
        self.assertEqual(
            msg_text_db.pay_slacker_reminder,
            'Leniwy przypominacz',
        )
        self.assertEqual(
            msg_text_db.blocked_user_text,
            'You are banned',
        )
        self.assertEqual(
            msg_text_db.ordering_is_blocked_text,
            'Ordering is Blocked',
        )

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_finance_mail_all_view(self):
        """
        Test finance emial to all view.
        """
        fill_db()
        resp = self.client.get('/finance_mail_all')
        self.assertEqual(resp.status_code, 200)
        with mail.record_messages() as outbox:
            data = {'send_mail': 'remind_all'}
            resp = self.client.post('/finance_mail_all', data=data)
            self.assertEquals(resp.status_code, 302)
            self.assertEqual(len(outbox), 2)
            msg = outbox[0]
            self.assertTrue(msg.subject.startswith('Lunch'))
            self.assertIn('February', msg.body)

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_payment_remind_view(self):
        """
        Test finance remind send email.
        """
        fill_db()
        with mail.record_messages() as outbox:
            resp = self.client.post('/payment_remind/x@x.pl/0')
            self.assertTrue(resp.status_code == 302)
            self.assertEqual(len(outbox), 1)
            msg = outbox[0]
            self.assertTrue(msg.subject.startswith('Lunch'))
            self.assertIn('reminder3', msg.body)
            self.assertEqual(msg.recipients, ['x@x.pl'])

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_finance_search_view(self):
        """
        Test finance serach view.
        """
        fill_db()
        resp = self.client.get('/finance_search')
        self.assertEqual(resp.status_code, 200)
        data = {'year': '2015', 'month': '1', 'did_pay': '0'}
        resp = self.client.post('/finance_search', data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp.location,
            'http://localhost/finance/2015/1/0',
        )

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_random_food(self):
        """
        Test random food.
        """
        fill_db()
        for i in range(4):
            order = Order()
            order.description = 'Kebab'
            order.company = 'Pod Koziołkiem'
            order.cost = 1
            order.user_name = 'test@user.pl'
            order.arrival_time = '12:00'
            db.session.add(order)
        for i in range(4):
            order = Order()
            order.description = 'Burger'
            order.company = 'Pod Koziołkiem'
            order.cost = 1
            order.user_name = 'test@user.pl'
            order.arrival_time = '12:00'
            db.session.add(order)
        for i in range(3):
            order = Order()
            order.description = 'Cieply_jamnik'
            order.company = 'Pod Koziołkiem'
            order.cost = 1
            order.user_name = 'test@user.pl'
            order.arrival_time = '12:00'
            db.session.add(order)
        for i in range(3):
            order = Order()
            order.description = 'Kosmata_szynka'
            order.company = 'Pod Koziołkiem'
            order.cost = 1
            order.user_name = 'test@user.pl'
            order.arrival_time = '12:00'
            db.session.add(order)
        order = Order()
        order.description = 'szpinak'
        order.company = 'Pod Koziołkiem'
        order.cost = 1
        order.user_name = 'test@user.pl'
        order.arrival_time = '12:00'
        db.session.add(order)
        db.session.commit()
        resp = self.client.get('/random_meal/1')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp.location,
            'http://localhost/order'
        )
        resp = self.client.get('/random_meal/2')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp.location,
            'http://localhost/order'
        )
        self.client.get('/random_meal/2')
        for i in range(10):
            orders = Order.query.filter(
                Order.user_name == 'test_user'
            ).all()
            for user_order in orders:
                self.assertNotEqual(
                    'szpinak',
                    user_order.description,
                )

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_send_daily_reminder(self):
        """
        Test sends daily reminder to all users.
        """
        fill_db()
        with mail.record_messages() as outbox:
            resp = self.client.get('/send_daily_reminder')
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(outbox), 1)
            msg = outbox[0]
            self.assertTrue(msg.subject.startswith('STX Lunch'))
            self.assertIn('daili1', msg.body)
            self.assertEqual(msg.recipients, ['reminder@user.pl'])

    def test_orders_summary_for_tv(self):
        """
        Test orders summary for tv view.
        """
        fill_db()
        resp = self.client.get('/tv')
        self.assertEqual(resp.status_code, 200)
        self.assertIn("test_user", str(resp.data))
        self.assertIn("Maly Gruby Nalesnik", str(resp.data))
        self.assertIn("Duzy Gruby Nalesnik", str(resp.data))

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_finance_block_user(self):
        """
        Test block user view.
        """
        fill_db()
        resp = self.client.get('/order')
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Tiramisu", str(resp.data))
        resp = self.client.get('/finance_block_user')
        self.assertEqual(resp.status_code, 200)

        # Test blocking
        data = {
            'user_select': '1',
            'block_change': 'block',
        }
        resp = self.client.post('/finance_block_user', data=data)
        self.assertEqual(resp.status_code, 302)
        user = User.query.get(1)
        self.assertIs(user.active, False)
        self.assertIs(user.is_active(), False)

        # Test unblocking
        data = {
            'user_select': '1',
            'block_change': 'unblock',
        }
        resp = self.client.post('/finance_block_user', data=data)
        self.assertEqual(resp.status_code, 302)
        user = User.query.get(1)
        self.assertTrue(user.active, True)
        self.assertTrue(user.is_active(), True)

        MOCK_ADMIN.active = False
        MOCK_ADMIN.is_active.return_value = False
        resp = self.client.get('/order')
        self.assertEqual(resp.status_code, 302)
        data = {
            'cost': '12',
            'company': 'Pod Koziołkiem',
            'description': 'blokowane_jedzonko',
            'send_me_a_copy': 'false',
            'arrival_time': '12:00',
        }
        resp = self.client.post('/order', data=data)
        self.assertEqual(resp.status_code, 302)
        order = Order.query.filter(
            Order.description == data['description']
        ).first()
        self.assertIs(order, None)

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_finance_block_ordering(self):
        """
        Test blocking and unblocking order ability for all users
        """
        fill_db()
        resp = self.client.get('/order')
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Tiramisu", str(resp.data))

        # test blocking
        resp = self.client.get('/finance_block_ordering')
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/order')
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn("Tiramisu", str(resp.data))
        data = {
            'cost': '12',
            'company': 'Pod Koziołkiem',
            'description': 'dobre_jedzonko',
            'send_me_a_copy': 'false',
            'arrival_time': '12:00',
        }
        resp = self.client.post('/order', data=data)
        self.assertEqual(resp.status_code, 302)

        # test unblocking
        resp = self.client.get('/finance_unblock_ordering')
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/order')
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Tiramisu", str(resp.data))

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def z_test_finance_block_user_acces(self):
        """
        Test if blocking really blocks user from accesing
        """
        allow_ordering()
        MOCK_ADMIN.active = False
        MOCK_ADMIN.is_active.return_value = False
        resp = self.client.get('/order')
        self.assertEqual(resp.status_code, 302)
        data = {
            'cost': '12',
            'company': 'Pod Koziołkiem',
            'description': 'dobre_jedzonko',
            'send_me_a_copy': 'false',
            'arrival_time': '12:00',
        }
        resp = self.client.post('/order', data=data)
        self.assertEqual(resp.status_code, 302)
        order = Order.query.get(1)
        self.assertIs(order, None)

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    @patch(
        'lunch_app.views.get_dania_dnia_from_pod_koziolek',
        new=MOCK_DATA_KOZIOLEK,
    )
    def test_add_daily_koziolek(self):
        """
        Test adding meal of a day from koziolek's webpage.
        """
        allow_ordering()
        resp = self.client.get('/add_daily_koziolek')
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/order')
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Danie dnia", str(resp.data))
        food = Food.query.filter(
            Food.description == 'Danie dnia Koziołek: 1.Kotlet schabowy z '
                                'ziemniakami gotowanymi i kapusta zasmażana'
        ).first()
        self.assertEqual(food.company, "Pod Koziołkiem")
        self.assertEqual(food.cost, 11)
        self.assertEqual(food.o_type, "daniednia")
        self.assertEqual(food.date_available_from, make_datetime(date.today()))
        self.assertEqual(food.date_available_to, make_datetime(date.today()))

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    @patch(
        'lunch_app.views.get_week_from_tomas',
        new=MOCK_DATA_TOMAS,
    )
    def test_get_week_from_tomas_view(self):
        """
        Test adding weak meals from Tomas.
        """
        allow_ordering()
        MOCK_ADMIN.active = True
        MOCK_ADMIN.is_active.return_value = True
        resp = self.client.get('/add_week_tomas')
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/order')
        self.assertEqual(resp.status_code, 200)
        self.assertIn("10.0 PLN", str(resp.data))
        self.assertIn("12.0 PLN", str(resp.data))
        self.assertIn("4.0 PLN", str(resp.data))

        # meal of a day from Monday
        food = Food.query.filter(
            Food.description == 'Kawałki kurczaka w sosie chińskim z '
                                'warzywami, ryż, sałata.'
        ).first()
        self.assertEqual(food.company, "Tomas")
        self.assertEqual(food.cost, 10)
        self.assertEqual(food.o_type, "daniednia")
        self.assertEqual(food.date_available_from, make_datetime(date.today()))
        self.assertEqual(food.date_available_to, make_datetime(date.today()))

        # meal and soup of a day from Thursday
        food = Food.query.filter(
            Food.description == 'żurek + Sałatka grillowanym mięsem, '
                                'warzywami i sosem czosnko.'
        ).first()
        self.assertEqual(food.company, "Tomas")
        self.assertEqual(food.cost, 12)
        self.assertEqual(food.o_type, "daniednia")
        self.assertEqual(
            food.date_available_from,
            make_datetime(date.today() + timedelta(3))
        )
        self.assertEqual(
            food.date_available_to,
            make_datetime(date.today() + timedelta(3))
        )

        # diet meal
        food = Food.query.filter(
            Food.description == 'ok.440kcal Polędwiczki drobiowe 120g,'
                                ' ryż 200g, bukiet warzyw 150g.'
        ).first()
        self.assertEqual(food.company, "Tomas")
        self.assertEqual(food.cost, 12)
        self.assertEqual(food.o_type, "tygodniowe")
        self.assertEqual(
            food.date_available_from,
            make_datetime(date.today())
        )
        self.assertEqual(
            food.date_available_to,
            make_datetime(date.today() + timedelta(4))
        )

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_order_pizza_for_everybody(self):
        """
        Test pizza ordering for everyone.
        """
        fill_db()
        with mail.record_messages() as outbox:
            resp = self.client.get('/order_pizza_for_everybody')
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(outbox), 2)
            msg = outbox[0]
            self.assertTrue(msg.subject.startswith('Lunch app PIZZA'))
            self.assertIn('pizza for everyone', msg.body)
            self.assertEqual(len(msg.recipients), 4)
        resp = self.client.get('/pizza_time/1')
        self.assertEqual(resp.status_code, 200)

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_pizza_time_view(self):
        """
        Test pizza showing menu, pizza ordering, and orders list.
        """
        fill_db()
        resp = self.client.get('/order_pizza_for_everybody')
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/pizza_time/1')
        self.assertEqual(resp.status_code, 200)
        data = {
            'description': 'WielkaMargarittaZKotem',
            'pizza_size': 'big',
        }
        resp = self.client.post('/pizza_time/1', data=data)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/pizza_time/1')
        self.assertIn('WielkaMargarittaZKotem', str(resp.data))
        data = {
            'description': 'WielkaMargarittaZMisiem',
            'pizza_size': 'big',
        }
        resp = self.client.post('/pizza_time/1', data=data)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/pizza_time/1')
        self.assertIn('You already ordered !', str(resp.data))
        self.assertNotIn('WielkaMargarittaZMisiem', str(resp.data))

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_pizza_time_stop(self):
        """
        Test pizza time stop function
        """
        fill_db()
        resp = self.client.get('/order_pizza_for_everybody')
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/pizza_time/1')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/pizza_time_stop/1')
        self.assertEqual(resp.status_code, 302)
        data = {
            'description': 'WielkaMargarittaZKotem',
            'pizza_size': 'big',
        }
        resp = self.client.post('/pizza_time/1', data=data)
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/pizza_time/1')
        self.assertNotIn('WielkaMargarittaZKotem', str(resp.data))


class LunchBackendUtilsTestCase(unittest.TestCase):
    """
    Utils tests.
    """
    def setUp(self):
        """
        Before each test, set up a environment.
        """
        pass

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_current_date(self):
        """
        Test current date.
        """
        self.assertEqual(utils.get_current_date(), date.today())

    def test_get_current_datetime(self):
        """
        Test current datetime.
        """
        self.assertAlmostEqual(
            utils.get_current_datetime(),
            datetime.now(),
            delta=timedelta(microseconds=101),
        )

    def test_make_date(self):
        """
        Test make date.
        """
        self.assertEqual(
            utils.make_date(datetime.now()),
            date.today()
        )

    def test_next_month(self):
        """
        Test next month function.
        """
        self.assertEqual(
            utils.next_month(2015, 12),
            (2016, 1),
        )
        self.assertEqual(
            utils.next_month(2015, 6),
            (2015, 7),
        )

    def test_previous_month(self):
        """
        Test previous month function.
        """
        self.assertEqual(
            utils.previous_month(2015, 1),
            (2014, 12),
        )
        self.assertEqual(
            utils.previous_month(2015, 6),
            (2015, 5),
        )


class LunchBackendPermissionsTestCase(unittest.TestCase):
    """
    Permissions tests.
    """
    def setUp(self):
        """
        Before each test, set up a environment.
        """
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_permissions(self):
        """
        Tests if permissions decorator works properly
        """
        resp = self.client.get('add_food')
        self.assertEqual(resp.status_code, 401)
        resp_2 = self.client.get('day_summary')
        self.assertEqual(resp_2.status_code, 401)


class LunchWebCrawlersTestCases(unittest.TestCase):
    """
    Webcrawlers tests.
    """
    def setUp(self):
        """
        Before each test, set up a environment.
        """
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    @patch(
        'lunch_app.webcrawler.read_webpage',
        new=MOCK_WWW_KOZIOLEK,
    )
    def test_get_dania_dnia_from_pod_koziolek(self):
        """
        Tests web crawling functions works properly Koziolek add meal of a day
        """
        data = get_dania_dnia_from_pod_koziolek()
        self.assertGreaterEqual(len(data), 2)
        self.assertGreaterEqual(len(data["zupa_dnia"]), 1)
        self.assertGreaterEqual(len(data['danie_dania_1']), 1)

    @patch(
        'lunch_app.webcrawler.read_webpage',
        new=MOCK_WWW_TOMAS,
    )
    def test_get_week_from_tomas(self):
        """
        Tests web crawling functions works properly for Tomas add weak
        """
        data = get_week_from_tomas()
        self.assertEqual(len(data), 6)
        self.assertGreaterEqual(len(data['diet']), 1)
        for i in range(1, 6):
            food = data['dzien_{}'.format(i)]
            self.assertEqual(len(food), 3, msg="ERROR IN {}".format(i))
            self.assertGreaterEqual(
                len(food['zupy']),
                1,
                msg="ERROR IN {}".format(i),
            )
            self.assertGreaterEqual(
                len(food['dania']),
                1,
                msg="ERROR IN {}".format(i),
            )
            self.assertGreaterEqual(
                len(food['zupa_i_dania']),
                1,
                msg="ERROR IN {}".format(i),
            )


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(LunchBackendViewsTestCase))
    base_suite.addTest(unittest.makeSuite(LunchBackendUtilsTestCase))
    base_suite.addTest(unittest.makeSuite(LunchBackendPermissionsTestCase))
    base_suite.addTest(unittest.makeSuite(LunchWebCrawlersTestCases))
    return base_suite


if __name__ == '__main__':
    unittest.main()
