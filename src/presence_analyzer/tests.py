# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest
from mock import patch

from presence_analyzer import main, utils, views


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=E1103, R0904
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
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
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view(self):
        """
        Test mean time weekday view.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        non_empty_data = [item for item in data if item[1] != 0]

        self.assertEqual(len(non_empty_data), 3)
        self.assertEqual(non_empty_data[0][0], 'Tue')

    @patch.object(views, 'log')
    def test_mean_time_weekday_user(self, mocked_log):
        """
        Test mean time weekday view with invalid user_id.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        mocked_log.debug.assert_called_with('User %s not found!', 1)

    def test_presence_weekday_view(self):
        """
        Test presence weekday view.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        expected_output = [[u'Weekday', u'Presence (s)'], [u'Mon', 0],
                           [u'Tue', 30047], [u'Wed', 24465], [u'Thu', 23705],
                           [u'Fri', 0], [u'Sat', 0], [u'Sun', 0]]
        self.assertEqual(data, expected_output)

    @patch.object(views, 'log')
    def test_presence_weekday_user(self, mocked_log):
        """
        Test presence weekday view with invalid user_id.
        """
        resp = self.client.get('/api/v1/presence_weekday/1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        mocked_log.debug.assert_called_with('User %s not found!', 1)

    @patch.object(views, 'log')
    def test_presence_start_end_user(self, mocked_log):
        """
        Test presence mean start and mean end time view with invalid user_id.
        """
        resp = self.client.get('/api/v1/presence_start_end/1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        mocked_log.debug.assert_called_with('User %s not found!', 1)

    def test_presence_start_end_view(self):
        """
        Test presence mean start and mean end time view.
        """
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        expected_output = [
            [u'Mon', 0, 0],
            [u'Tue', 34745, 64792],
            [u'Wed', 33592, 58057],
            [u'Thu', 38926, 62631],
            [u'Fri', 0, 0],
            [u'Sat', 0, 0],
            [u'Sun', 0, 0],
        ]
        self.assertEqual(data, expected_output)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))
        self.assertEqual(len(data[11]), 5)

    def test_interval(self):
        """
        Test interval method.
        """
        self.assertEqual(utils.interval(datetime.time(9, 39, 5),
                                        datetime.time(17, 59, 52)), 30047)
        self.assertEqual(utils.interval(datetime.time(0, 0, 0),
                                        datetime.time(0, 0, 0)), 0)
        self.assertEqual(utils.interval(datetime.time(0, 0, 10),
                                        datetime.time(0, 0, 5)), -5)

    def test_group_by_weekday(self):
        """
        Test grouping by weekday.
        """
        data = utils.get_data()
        weekdays = utils.group_by_weekday(data[10])
        expected_output = {
            0: [],
            1: [30047],
            2: [24465],
            3: [23705],
            4: [],
            5: [],
            6: [],
        }
        self.assertEqual(weekdays, expected_output)

    def test_mean(self):
        """
        Test mean method.
        """
        self.assertEqual(utils.mean([22999, 22969]), 22984)
        self.assertEqual(utils.mean([]), 0)
        self.assertEqual(utils.mean([1]), 1)

    def test_group_by_weekday_start_end(self):
        """
        Test grouping start and end presences by weekday.
        """
        data = utils.get_data()
        weekdays = utils.group_by_weekday_start_end(data[10])
        expected_output = {
            0: {'start': [], 'end': []},
            1: {'start': [34745], 'end': [64792]},
            2: {'start': [33592], 'end': [58057]},
            3: {'start': [38926], 'end': [62631]},
            4: {'start': [], 'end': []},
            5: {'start': [], 'end': []},
            6: {'start': [], 'end': []},
        }
        self.assertEqual(weekdays, expected_output)

    def test_presence_start_end(self):
        """
        Test grouping mean start and mean end presences by weekday.
        """
        data = utils.get_data()
        weekdays = utils.presence_start_end(data[10])
        expected_output = {
            0: {'start': 0, 'end': 0},
            1: {'start': 34745, 'end': 64792},
            2: {'start': 33592, 'end': 58057},
            3: {'start': 38926, 'end': 62631},
            4: {'start': 0, 'end': 0},
            5: {'start': 0, 'end': 0},
            6: {'start': 0, 'end': 0},
        }

        self.assertEqual(weekdays, expected_output)


def suite():
    """
    Default test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    test_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.main()
