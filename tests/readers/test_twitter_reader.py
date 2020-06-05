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

from unittest import TestCase, mock
from freezegun import freeze_time

from datetime import datetime, timedelta

from nck.readers.twitter_reader import TwitterReader


class TwitterReaderTest(TestCase):
    def mock_twitter_reader(self, **kwargs):
        for param, value in kwargs.items():
            if param == "end_date":
                setattr(self, param, value + timedelta(days=1))
            else:
                setattr(self, param, value)
        setattr(self, "account", mock.MagicMock())

    @mock.patch.object(TwitterReader, "__init__", mock_twitter_reader)
    def test_get_daily_period_items(self):
        kwargs = {"start_date": datetime(2020, 1, 1), "end_date": datetime(2020, 1, 3)}
        output = TwitterReader(**kwargs).get_daily_period_items()
        expected = [datetime(2020, 1, 1), datetime(2020, 1, 2), datetime(2020, 1, 3)]
        self.assertEqual(output, expected)

    @mock.patch.object(TwitterReader, "__init__", mock_twitter_reader)
    def test_parse_with_total_granularity(self):
        kwargs = {"granularity": "TOTAL", "segmentation_type": None}
        raw_analytics_response = {
            "data": [
                {
                    "id": "XXXXX",
                    "id_data": [
                        {"segment": None, "metrics": {"retweets": [11], "likes": [12]}}
                    ],
                },
                {
                    "id": "YYYYY",
                    "id_data": [
                        {"segment": None, "metrics": {"retweets": [21], "likes": [22]}}
                    ],
                },
            ],
        }
        output = TwitterReader(**kwargs).parse(raw_analytics_response)
        expected = [
            {"id": "XXXXX", "retweets": 11, "likes": 12},
            {"id": "YYYYY", "retweets": 21, "likes": 22},
        ]
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)

    @mock.patch.object(TwitterReader, "__init__", mock_twitter_reader)
    def test_parse_with_day_granularity(self):
        kwargs = {
            "granularity": "DAY",
            "segmentation_type": None,
            "start_date": datetime(2020, 1, 1),
            "end_date": datetime(2020, 1, 3),
        }
        raw_analytics_response = {
            "data": [
                {
                    "id": "XXXXX",
                    "id_data": [
                        {
                            "segment": None,
                            "metrics": {
                                "retweets": [11, 12, 13],
                                "likes": [14, 15, 16],
                            },
                        }
                    ],
                },
                {
                    "id": "YYYYY",
                    "id_data": [
                        {
                            "segment": None,
                            "metrics": {
                                "retweets": [21, 22, 23],
                                "likes": [24, 25, 26],
                            },
                        }
                    ],
                },
            ],
        }
        output = TwitterReader(**kwargs).parse(raw_analytics_response)
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

    @mock.patch.object(TwitterReader, "__init__", mock_twitter_reader)
    def test_parse_with_segment(self):
        kwargs = {"granularity": "TOTAL", "segmentation_type": "GENDER"}
        raw_analytics_response = {
            "data": [
                {
                    "id": "XXXXX",
                    "id_data": [
                        {
                            "segment": {"segment_name": "Male"},
                            "metrics": {"retweets": [11], "likes": [12]},
                        },
                        {
                            "segment": {"segment_name": "Female"},
                            "metrics": {"retweets": [13], "likes": [14]},
                        },
                    ],
                },
                {
                    "id": "YYYYY",
                    "id_data": [
                        {
                            "segment": {"segment_name": "Male"},
                            "metrics": {"retweets": [21], "likes": [22]},
                        },
                        {
                            "segment": {"segment_name": "Female"},
                            "metrics": {"retweets": [23], "likes": [24]},
                        },
                    ],
                },
            ],
        }
        output = TwitterReader(**kwargs).parse(raw_analytics_response)
        expected = [
            {"id": "XXXXX", "gender": "Male", "retweets": 11, "likes": 12},
            {"id": "XXXXX", "gender": "Female", "retweets": 13, "likes": 14},
            {"id": "YYYYY", "gender": "Male", "retweets": 21, "likes": 22},
            {"id": "YYYYY", "gender": "Female", "retweets": 23, "likes": 24},
        ]
        for output_record, expected_record in zip(output, expected):
            self.assertDictEqual(output_record, expected_record)

    @freeze_time("2020-01-01")
    @mock.patch.object(TwitterReader, "__init__", mock_twitter_reader)
    def test_add_date_if_necessary(self):
        kwargs = {
            "report_type": "ANALYTICS",
            "granularity": "TOTAL",
            "start_date": datetime(2020, 1, 1),
            "end_date": datetime(2020, 1, 3),
            "add_request_date_to_report": True,
        }
        record = {"id": "XXXXX", "name": "Artefact Campaign"}
        output = TwitterReader(**kwargs).add_date_if_necessary(record)
        expected = {
            "id": "XXXXX",
            "name": "Artefact Campaign",
            "period_start_date": "2020-01-01",
            "period_end_date": "2020-01-03",
            "request_date": "2020-01-01",
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

    @mock.patch.object(TwitterReader, "__init__", mock_twitter_reader)
    @mock.patch.object(
        TwitterReader, "get_active_entity_ids", lambda *args: ["XXXXX", "YYYYYY"]
    )
    @mock.patch.object(TwitterReader, "get_job_ids", lambda *args: ["123456789"])
    @mock.patch.object(TwitterReader, "get_job_result", mock_get_job_result)
    @mock.patch.object(TwitterReader, "get_raw_analytics_response", lambda *args: {})
    @mock.patch.object(TwitterReader, "parse", mock_parse)
    def test_read_analytics_report(self):
        kwargs = {
            "report_type": "ANALYTICS",
            "granularity": "DAY",
            "add_request_date_to_report": False,
        }
        output = next(TwitterReader(**kwargs).read())
        expected = [
            {"id": "XXXXX", "retweets": 11, "likes": 12},
            {"id": "YYYYY", "retweets": 21, "likes": 22},
        ]
        for output_record, expected_record in zip(output.readlines(), iter(expected)):
            self.assertEqual(output_record, expected_record)
