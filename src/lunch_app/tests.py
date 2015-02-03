# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
# pylint: disable=maybe-no-member, too-many-public-methods, invalid-name

from datetime import datetime, date, timedelta
import os.path
import unittest
from unittest.mock import Mock, patch

from .main import app, db, mail
from . import main, utils
from .fixtures import fill_db
from .models import Order, Food, MailText


MOCK_ADMIN = Mock()
MOCK_ADMIN.is_admin.return_value = True
MOCK_ADMIN.username = 'test_user'
MOCK_ADMIN.is_anonymous.return_value = False
MOCK_ADMIN.email = 'mock@mock.com'


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
        resp = self.client.get('/info')
        self.assertEqual(resp.status_code, 200)

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
        }
        resp_2 = self.client.post('/add_food', data=data)
        food_db = Food.query.first()
        self.assertTrue(resp_2.status_code == 302)
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
    def test_day_summary_view(self):
        """
        Test day summary page.
        """
        resp = self.client.get('/day_summary')
        self.assertEqual(resp.status_code, 200)
        order = Order()
        order.date = date.today()
        order.description = 'Duzy Gruby Nalesnik'
        order.company = 'Tomas'
        order.cost = 123
        order.user_name = 'test_user'
        order.arrival_time = '12:00'
        order_2 = Order()
        order_2.date = date.today()
        order_2.description = 'Maly Gruby Nalesnik'
        order_2.company = 'Tomas'
        order_2.cost = 223
        order_2.user_name = 'test_user'
        order_2.arrival_time = '13:00'
        db.session.add(order)
        db.session.add(order_2)
        db.session.commit()
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
            'daily_reminder_subject': 'STX Lunch nowy temat',
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

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_finance_mail_all_view(self):
        """
        Test finance emial to all view.
        """
        fill_db()
        resp = self.client.get('/finance_mail_all')
        self.assertEqual(resp.status_code, 200)
        with mail.record_messages() as outbox:
            resp = self.client.post('/finance_mail_all')
            self.assertTrue(resp.status_code == 302)
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
        resp = self.client.get('/random_meal')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp.location,
            'http://localhost/order'
        )
        for i in range(10):
            user_order = Order.query.filter(
                Order.user_name == 'test_user'
            ).first()
            self.assertNotEqual(
                'szpinak',
                user_order.description,
            )

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_send_daily_reminder(self):
        """
        Test sends daili reminder to all users.
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
        Test next month function
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
        Test previous month function
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


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(LunchBackendViewsTestCase))
    base_suite.addTest(unittest.makeSuite(LunchBackendUtilsTestCase))
    base_suite.addTest(unittest.makeSuite(LunchBackendPermissionsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
