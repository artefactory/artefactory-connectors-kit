import datetime
import unittest
from unittest import mock

from nck.readers.dbm_reader import DbmReader


class TestDbmReader(unittest.TestCase):

    def mock_dbm_reader(self, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)

    @mock.patch.object(DbmReader, '__init__', mock_dbm_reader)
    def test_get_query_body(self):
        kwargs = {}
        reader = DbmReader(**kwargs)
        reader.kwargs = {
            'filter': [('FILTER_ADVERTISER', 1)]
        }

        expected_query_body = {
            'metadata': {
                'format': 'CSV',
                'title': 'NO_TITLE_GIVEN',
                'dataRange': 'LAST_7_DAYS'
            },
            'params': {
                'type': 'TYPE_TRUEVIEW',
                'groupBys': None,
                'metrics': None,
                'filters': [
                    {
                        'type': 'FILTER_ADVERTISER',
                        'value': '1'
                    }
                ]
            },
            'schedule': {
                'frequency': 'ONE_TIME'
            }
        }

        self.assertDictEqual(reader.get_query_body(), expected_query_body)

    @mock.patch.object(DbmReader, '__init__', mock_dbm_reader)
    def test_get_query_body_ms_conversion(self):
        kwargs = {}
        reader = DbmReader(**kwargs)
        reader.kwargs = {
            'filter': [('FILTER_ADVERTISER', 1)],
            'start_date': datetime.datetime(2020, 1, 15),
            'end_date': datetime.datetime(2020, 1, 18)
        }

        expected_query_body = {
            'metadata': {
                'format': 'CSV',
                'title': 'NO_TITLE_GIVEN',
                'dataRange': 'CUSTOM_DATES'
            },
            'params': {
                'type': 'TYPE_TRUEVIEW',
                'groupBys': None,
                'metrics': None,
                'filters': [
                    {
                        'type': 'FILTER_ADVERTISER',
                        'value': '1'
                    }
                ]
            },
            'schedule': {
                'frequency': 'ONE_TIME'
            },
            'reportDataStartTimeMs': 1579129200000,
            'reportDataEndTimeMs': 1579388400000
        }
        self.assertDictEqual(reader.get_query_body(), expected_query_body)
