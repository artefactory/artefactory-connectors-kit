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

from datetime import datetime
from unittest import TestCase, mock

from click import ClickException
from freezegun import freeze_time
from nck.readers.twitter.reader import TwitterReader
from nck.utils.exceptions import DateDefinitionException
from twitter_ads.client import Client


class TwitterReaderTest(TestCase):

    kwargs = {
        "consumer_key": "",
        "consumer_secret": "",
        "access_token": "",
        "access_token_secret": "",
        "account_id": "",
        "report_type": None,
        "entity": None,
        "entity_attribute": [],
        "granularity": None,
        "metric_group": [],
        "placement": None,
        "segmentation_type": None,
        "platform": None,
        "country": None,
        "add_request_date_to_report": None,
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2020, 1, 3),
        "date_range": None,
    }

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_validate_dates(self):
        temp_kwargs = self.kwargs.copy()
        params = {"start_date": datetime(2020, 1, 3), "end_date": datetime(2020, 1, 1)}
        temp_kwargs.update(params)
        with self.assertRaises(DateDefinitionException):
            TwitterReader(**temp_kwargs)

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_validate_analytics_segmentation_if_missing_platform(self):
        temp_kwargs = self.kwargs.copy()
        params = {
            "report_type": "ANALYTICS",
            "segmentation_type": "DEVICES",
            "platform": None,
        }
        temp_kwargs.update(params)
        with self.assertRaises(ClickException):
            TwitterReader(**temp_kwargs)

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_validate_analytics_segmentation_if_missing_country(self):
        temp_kwargs = self.kwargs.copy()
        params = {
            "report_type": "ANALYTICS",
            "segmentation_type": "CITIES",
            "country": None,
        }
        temp_kwargs.update(params)
        with self.assertRaises(ClickException):
            TwitterReader(**temp_kwargs)

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_validate_analytics_metric_groups_if_funding_instrument(self):
        temp_kwargs = self.kwargs.copy()
        params = {
            "report_type": "ANALYTICS",
            "entity": "FUNDING_INSTRUMENT",
            "metric_group": ["ENGAGEMENT", "VIDEO"],
        }
        temp_kwargs.update(params)
        with self.assertRaises(ClickException):
            TwitterReader(**temp_kwargs)

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_validate_analytics_metric_groups_if_mobile_conversion(self):
        temp_kwargs = self.kwargs.copy()
        params = {
            "report_type": "ANALYTICS",
            "metric_group": ["MOBILE_CONVERSION", "ENGAGEMENT"],
        }
        temp_kwargs.update(params)
        with self.assertRaises(ClickException):
            TwitterReader(**temp_kwargs)

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_validate_analytics_entity(self):
        temp_kwargs = self.kwargs.copy()
        params = {"report_type": "ANALYTICS", "entity": "CARD"}
        temp_kwargs.update(params)
        with self.assertRaises(ClickException):
            TwitterReader(**temp_kwargs)

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_validate_reach_entity(self):
        temp_kwargs = self.kwargs.copy()
        params = {"report_type": "REACH", "entity": "LINE_ITEM"}
        temp_kwargs.update(params)
        with self.assertRaises(ClickException):
            TwitterReader(**temp_kwargs)

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_validate_entity_attributes(self):
        temp_kwargs = self.kwargs.copy()
        params = {
            "report_type": "ENTITY",
            "entity": "CAMPAIGN",
            "entity_attribute": ["id", "name", "XXXXX"],
        }
        temp_kwargs.update(params)
        with self.assertRaises(ClickException):
            TwitterReader(**temp_kwargs)

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_get_daily_period_items(self):
        temp_kwargs = self.kwargs.copy()
        params = {"start_date": datetime(2020, 1, 1), "end_date": datetime(2020, 1, 3)}
        temp_kwargs.update(params)
        output = TwitterReader(**temp_kwargs).get_daily_period_items()
        expected = [datetime(2020, 1, 1), datetime(2020, 1, 2), datetime(2020, 1, 3)]
        self.assertEqual(output, expected)

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_parse_with_total_granularity(self):
        temp_kwargs = self.kwargs.copy()
        params = {"granularity": "TOTAL", "segmentation_type": None}
        temp_kwargs.update(params)
        raw_analytics_response = {
            "time_series_length": 1,
            "data": [
                {"id": "XXXXX", "id_data": [{"segment": None, "metrics": {"retweets": [11], "likes": [12]}}]},
                {"id": "YYYYY", "id_data": [{"segment": None, "metrics": {"retweets": [21], "likes": [22]}}]},
            ],
        }
        output = TwitterReader(**temp_kwargs).parse(raw_analytics_response)
        expected = [
            {"id": "XXXXX", "retweets": 11, "likes": 12},
            {"id": "YYYYY", "retweets": 21, "likes": 22},
        ]
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_parse_with_day_granularity(self):
        temp_kwargs = self.kwargs.copy()
        params = {
            "granularity": "DAY",
            "segmentation_type": None,
            "start_date": datetime(2020, 1, 1),
            "end_date": datetime(2020, 1, 3),
        }
        temp_kwargs.update(params)
        raw_analytics_response = {
            "time_series_length": 3,
            "data": [
                {"id": "XXXXX", "id_data": [{"segment": None, "metrics": {"retweets": [11, 12, 13], "likes": [14, 15, 16]}}]},
                {"id": "YYYYY", "id_data": [{"segment": None, "metrics": {"retweets": [21, 22, 23], "likes": [24, 25, 26]}}]},
            ],
        }
        output = TwitterReader(**temp_kwargs).parse(raw_analytics_response)
        expected = [
            {"date": "2020-01-01", "id": "XXXXX", "retweets": 11, "likes": 14},
            {"date": "2020-01-02", "id": "XXXXX", "retweets": 12, "likes": 15},
            {"date": "2020-01-03", "id": "XXXXX", "retweets": 13, "likes": 16},
            {"date": "2020-01-01", "id": "YYYYY", "retweets": 21, "likes": 24},
            {"date": "2020-01-02", "id": "YYYYY", "retweets": 22, "likes": 25},
            {"date": "2020-01-03", "id": "YYYYY", "retweets": 23, "likes": 26},
        ]
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_parse_with_segment(self):
        temp_kwargs = self.kwargs.copy()
        params = {"granularity": "TOTAL", "segmentation_type": "GENDER"}
        temp_kwargs.update(params)
        raw_analytics_response = {
            "time_series_length": 1,
            "data": [
                {
                    "id": "XXXXX",
                    "id_data": [
                        {"segment": {"segment_name": "Male"}, "metrics": {"retweets": [11], "likes": [12]}},
                        {"segment": {"segment_name": "Female"}, "metrics": {"retweets": [13], "likes": [14]}},
                    ],
                },
                {
                    "id": "YYYYY",
                    "id_data": [
                        {"segment": {"segment_name": "Male"}, "metrics": {"retweets": [21], "likes": [22]}},
                        {"segment": {"segment_name": "Female"}, "metrics": {"retweets": [23], "likes": [24]}},
                    ],
                },
            ],
        }
        output = TwitterReader(**temp_kwargs).parse(raw_analytics_response)
        expected = [
            {"id": "XXXXX", "gender": "Male", "retweets": 11, "likes": 12},
            {"id": "XXXXX", "gender": "Female", "retweets": 13, "likes": 14},
            {"id": "YYYYY", "gender": "Male", "retweets": 21, "likes": 22},
            {"id": "YYYYY", "gender": "Female", "retweets": 23, "likes": 24},
        ]
        for output_record, expected_record in zip(output, expected):
            self.assertDictEqual(output_record, expected_record)

    @freeze_time("2020-01-03")
    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    def test_add_request_or_period_dates(self):
        temp_kwargs = self.kwargs.copy()
        params = {
            "report_type": "ANALYTICS",
            "granularity": "TOTAL",
            "start_date": datetime(2020, 1, 1),
            "end_date": datetime(2020, 1, 3),
            "add_request_date_to_report": True,
        }
        temp_kwargs.update(params)
        record = {"id": "XXXXX", "name": "Artefact Campaign"}
        output = TwitterReader(**temp_kwargs).add_request_or_period_dates(record)
        expected = {
            "id": "XXXXX",
            "name": "Artefact Campaign",
            "period_start_date": "2020-01-01",
            "period_end_date": "2020-01-03",
            "request_date": "2020-01-03",
        }
        self.assertEqual(output, expected)

    def mock_get_job_result(*args):
        job_result = mock.MagicMock()
        job_result.status = "SUCCESS"
        return job_result

    def mock_parse(*args):
        yield from [
            {"id": "XXXXX", "retweets": 11, "likes": 12},
            {"id": "YYYYY", "retweets": 21, "likes": 22},
        ]

    @mock.patch.object(Client, "__init__", lambda *args: None)
    @mock.patch.object(Client, "accounts", lambda *args: None)
    @mock.patch.object(TwitterReader, "get_active_entity_ids", lambda *args: ["XXXXX", "YYYYYY"])
    @mock.patch.object(TwitterReader, "get_job_ids", lambda *args: ["123456789"])
    @mock.patch.object(TwitterReader, "get_job_result", mock_get_job_result)
    @mock.patch.object(TwitterReader, "get_raw_analytics_response", lambda *args: {})
    @mock.patch.object(TwitterReader, "parse", mock_parse)
    def test_read_analytics_report(self):
        temp_kwargs = self.kwargs.copy()
        params = {
            "report_type": "ANALYTICS",
            "granularity": "DAY",
            "add_request_date_to_report": False,
        }
        temp_kwargs.update(params)
        reader = TwitterReader(**temp_kwargs)
        reader.account = mock.MagicMock()
        output = next(reader.read())
        expected = [
            {"id": "XXXXX", "retweets": 11, "likes": 12},
            {"id": "YYYYY", "retweets": 21, "likes": 22},
        ]
        for output_record, expected_record in zip(output.readlines(), iter(expected)):
            self.assertEqual(output_record, expected_record)
