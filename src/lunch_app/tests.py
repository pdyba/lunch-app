# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import datetime
import os.path
import unittest
from flask.ext.login import login_user, current_user

from lunch_app import main, db, app
from lunch_app import utils

# pylint: disable=maybe-no-member, too-many-public-methods
from lunch_app.forms import OrderForm
from lunch_app.models import User, Order


def setUp():
    test_config = os.path.join(
        os.path.dirname(__file__),
        '..', '..', 'parts', 'etc', 'test.cfg',
    )
    main.app.config['WTF_CSRF_ENABLED'] = False
    main.app.config.from_pyfile(test_config)
    main.init()
    db.create_all()
    db.init_app(app)
    db.reflect(app=app)


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
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_info_view(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/info')
        self.assertEqual(resp.status_code, 200)

    def test_my_orders_view(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/info')
        self.assertEqual(resp.status_code, 200)

    def test_overview_view(self):
        """
        Test overview page.
        """
        resp = self.client.get('/overview')
        self.assertEqual(resp.status_code, 200)

    def test_create_order_view(self):
        """
        Test create order page.
        """
        resp = self.client.get('/order')
        self.assertEqual(resp.status_code, 200)
        order = Order
        order.arrival_time = '12:00'
        order.company = 'Tomas'
        order.cost = 12
        order.description = 'dobre jedzenie'
        order.date = datetime.date.today()
        order.user_name = 'test_user'
        db.session.add(order)
        db.session.commit()
        order_db = Order.query.filter(Order.user_name == 'test_user').first()
        self.assertEquals(order.date, order_db.date)

    def test_add_food_view(self):
        """
        Test add food page.
        """
        resp = self.client.get('/add_food')
        self.assertEqual(resp.status_code, 200)

    def test_day_summary_view(self):
        """
        Test add food page.
        """
        resp = self.client.get('/day_summary')
        self.assertEqual(resp.status_code, 200)


class LunchBackendUtilsTestCase(unittest.TestCase):
    """
    Views tests.
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
        self.assertEquals(utils.get_current_date(), datetime.date.today())

    def test_get_current_datetime(self):
        """
        Test current datetime.
        """
        self.assertAlmostEqual(
            utils.get_current_datetime(),
            datetime.datetime.now(),
            delta=(datetime.timedelta(microseconds=101)),
        )

    def test_make_date(self):
        """
        Test make date.
        """

        self.assertEquals(
            utils.make_date(datetime.datetime.now()),
            datetime.date.today()
        )


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(LunchBackendViewsTestCase))
    base_suite.addTest(unittest.makeSuite(LunchBackendUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
