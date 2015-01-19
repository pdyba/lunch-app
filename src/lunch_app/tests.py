# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import datetime
import unittest

from lunch_app import main
from lunch_app import utils

# pylint: disable=maybe-no-member, too-many-public-methods


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

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        print(resp)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers['Location'].endswith('/overview'))

    def test_overview(self):
        """
        Test overview page.
        """
        resp = self.client.get('/overview')
        self.assertEqual(resp.status_code, 500)

    def test_create_order(self):
        """
        Test create order page.
        """
        resp = self.client.get('/order')
        self.assertEqual(resp.status_code, 500)

    def test_add_food(self):
        """
        Test add food page.
        """
        resp = self.client.get('/add_food')
        self.assertEqual(resp.status_code, 500)

    def test_day_summary(self):
        """
        Test add food page.
        """
        resp = self.client.get('/day_summary')
        self.assertEqual(resp.status_code, 500)


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
