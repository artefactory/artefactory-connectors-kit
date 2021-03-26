# GNU Lesser General Public License v3.0 only
# Copyright (C) 2020 Artefact
# licence-information@artefact.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import datetime
import unittest
from unittest import mock

from ack.readers.google_dbm.reader import GoogleDBMReader


class TestGoogleDBMReader(unittest.TestCase):
    def mock_dbm_reader(self, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)

    @mock.patch.object(GoogleDBMReader, "__init__", mock_dbm_reader)
    def test_get_query_body(self):
        kwargs = {}
        reader = GoogleDBMReader(**kwargs)
        reader.kwargs = {"filter": [("FILTER_ADVERTISER", 1)]}

        expected_query_body = {
            "kind": "doubleclickbidmanager#query",
            "metadata": {"format": "CSV", "title": "NO_TITLE_GIVEN", "dataRange": "LAST_7_DAYS"},
            "params": {
                "type": "TYPE_TRUEVIEW",
                "groupBys": [],
                "metrics": [],
                "filters": [{"type": "FILTER_ADVERTISER", "value": "1"}],
            },
            "schedule": {"frequency": "ONE_TIME"},
        }

        self.assertDictEqual(reader.get_query_body(), expected_query_body)

    @mock.patch.object(GoogleDBMReader, "__init__", mock_dbm_reader)
    def test_get_query_body_ms_conversion(self):
        kwargs = {}
        reader = GoogleDBMReader(**kwargs)
        reader.kwargs = {
            "filter": [("FILTER_ADVERTISER", 1)],
            "start_date": datetime.datetime(2020, 1, 15, tzinfo=datetime.timezone.utc),
            "end_date": datetime.datetime(2020, 1, 18, tzinfo=datetime.timezone.utc),
        }

        expected_query_body = {
            "kind": "doubleclickbidmanager#query",
            "metadata": {"format": "CSV", "title": "NO_TITLE_GIVEN", "dataRange": "CUSTOM_DATES"},
            "params": {
                "type": "TYPE_TRUEVIEW",
                "groupBys": [],
                "metrics": [],
                "filters": [{"type": "FILTER_ADVERTISER", "value": "1"}],
            },
            "schedule": {"frequency": "ONE_TIME"},
            "reportDataStartTimeMs": 1579132800000,
            "reportDataEndTimeMs": 1579392000000,
        }
        self.assertDictEqual(reader.get_query_body(), expected_query_body)
