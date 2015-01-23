# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
from datetime import datetime, date, timedelta
import os.path
import unittest
from unittest.mock import Mock, patch

from lunch_app import main, db, app
from lunch_app import utils

# pylint: disable=maybe-no-member, too-many-public-methods

# pylint: disable=maybe-no-member, too-many-public-methods, invalid-name

from lunch_app.models import Order, Food, User

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
    main.app.config.from_pyfile(test_config)
    main.app.config['WTF_CSRF_ENABLED'] = False
    main.init()
    db.init_app(app)
    db.create_all()


class LunchBackendViewsTestCase(unittest.TestCase):
    """
    Views tests.
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
            'cost': 12,
            'company': 'Pod Koziołkiem',
            'description': 'dobre_jedzonko',
            'send_me_a_copy': 'false',
            'date': '2015-01-01',
            'arrival_time': '12:00',
        }
        resp = self.client.post('/order', data=data)
        order_db = Order.query.filter(
            Order.description == 'dobre_jedzonko'
        ).first()
        self.assertTrue(resp.status_code == 302)
        self.assertEqual(order_db.cost, 12)
        self.assertEqual(order_db.company, 'Pod Koziołkiem')
        self.assertEqual(order_db.description, 'dobre_jedzonko')
        self.assertEqual(order_db.date, datetime(2015, 1, 1, 0, 0))
        self.assertEqual(order_db.arrival_time, '12:00')

    @patch('lunch_app.views.current_user', new=MOCK_ADMIN)
    def test_create_order_with_email(self):
        """
        Test create order with send me an email.
        """
        data = {
            'cost': 13,
            'company': 'Pod Koziołkiem',
            'description': 'To jest TESTow zamowienie dla emaila',
            'send_me_a_copy': 'true',
            'date': '2015-01-02',
            'arrival_time': '13:00',
        }

        resp = self.client.post('/order', data=data)
        order_db = Order.query.filter(
            Order.description == 'To jest TESTow zamowienie dla emaila'
        ).first()
        self.assertTrue(resp.status_code == 302)
        self.assertEqual(order_db.cost, 13)
        self.assertEqual(order_db.company, 'Pod Koziołkiem')
        self.assertEqual(
            order_db.description,
            'To jest TESTow zamowienie dla emaila',
        )
        self.assertEqual(order_db.date, datetime(2015, 1, 2, 0, 0))
        self.assertEqual(order_db.arrival_time, '13:00')
        self.assertEqual(order_db.user_name, 'test_user')

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_add_food_view(self):
        """
        Test add food page.
        """
        resp = self.client.get('/add_food')
        self.assertEqual(resp.status_code, 200)
        data = {
            'cost': 333,
            'description': 'dobre_jedzonko',
            'date_available_to': '2015-01-01',
            'company': 'Pod Koziołkiem',
            'date_available_from': '2015-01-01',
        }
        resp_2 = self.client.post('/add_food', data=data)
        food_db = Food.query.filter(
            Food.description == 'dobre_jedzonko'
        ).first()
        self.assertTrue(resp_2.status_code == 302)
        self.assertEqual(food_db.cost, 333)
        self.assertEqual(food_db.description, 'dobre_jedzonko')
        self.assertEqual(food_db.date_available_to, datetime(2015, 1, 1, 0, 0))
        self.assertEqual(food_db.company, 'Pod Koziołkiem')
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
        self.assertTrue('Maly Gruby Nalesnik' in resp.data.__str__())
        self.assertTrue('Duzy Gruby Nalesnik' in resp.data.__str__())
        db.session.close()

    def test_order_list_view(self):
        """
        Test order list page.
        """
        resp = self.client.get('/order_list')
        self.assertEqual(resp.status_code, 200)
        user = User()
        user.id = 1
        user.email = 'e@e.pl'
        user.username = 'test_user'
        db.session.add(user)
        db.session.commit()
        data = {'year': '2015', 'user': '1'}
        resp = self.client.post('/order_list', data=data)
        print(resp.data)
        self.assertEqual(resp.status_code, 302)
        self.assertEquals(resp.location, 'http://localhost/order_list/1/2015')
        data = {'year': '2015', 'month': '1', 'user': '1'}
        resp = self.client.post('/order_list', data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertEquals(
            resp.location,
            'http://localhost/order_list/1/2015/1'
        )

    @patch('lunch_app.permissions.current_user', new=MOCK_ADMIN)
    def test_edit_order_view(self):
        """
        Test edit order page.
        """
        order = Order()
        order.date = date.today()
        order.description = 'Duzy Gruby Nalesnik'
        order.company = 'Tomas'
        order.cost = 123
        order.user_name = 'test_user'
        order.arrival_time = '12:00'
        db.session.add(order)
        db.session.commit()
        resp = self.client.get('/order_edit/1/')
        self.assertEqual(resp.status_code, 200)
        data = {
            'cost': 12,
            'company': 'Pod Koziołkiem',
            'description': 'dobre_jedzonko',
            'send_me_a_copy': 'false',
            'date': '2015-01-01',
            'arrival_time': '12:00',
        }
        resp = self.client.post('/order_edit/1/', data=data)
        order_db = Order.query.filter(
            Order.description == 'dobre_jedzonko'
        ).first()
        self.assertTrue(resp.status_code == 302)
        self.assertEqual(order_db.cost, 12)
        self.assertEqual(order_db.company, 'Pod Koziołkiem')
        self.assertEqual(order_db.description, 'dobre_jedzonko')
        self.assertEqual(order_db.date, datetime(2015, 1, 1, 0, 0))
        self.assertEqual(order_db.arrival_time, '12:00')

    def test_company_summary_view(self):
        """
        Test company summary page.
        """
        resp = self.client.get('/company_summary')
        self.assertEqual(resp.status_code, 200)
        data = {'year': '2015', 'month': '1'}
        resp = self.client.post('/company_summary', data=data)
        print(resp.data)
        self.assertEqual(resp.status_code, 302)
        self.assertEquals(
            resp.location,
            'http://localhost/company_summary/2015/1',
        )
        resp = self.client.get('/company_summary/2015/1')
        self.assertEqual(resp.status_code, 200)


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
        self.assertEquals(utils.get_current_date(), date.today())

    def test_get_current_datetime(self):
        """
        Test current datetime.
        """
        self.assertAlmostEqual(
            utils.get_current_datetime(),
            datetime.now(),
            delta=(timedelta(microseconds=101)),
        )

    def test_make_date(self):
        """
        Test make date.
        """
        self.assertEquals(
            utils.make_date(datetime.now()),
            date.today()
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
