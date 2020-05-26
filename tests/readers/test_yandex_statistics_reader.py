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

import click
from parameterized import parameterized

from nck.readers.yandex_statistics_reader import YandexStatisticsReader


class TestYandexStatisticsReader(unittest.TestCase):

    @parameterized.expand([
        (
            "ALL_TIME",
            {
                "report_language": "en",
                "filters": (),
                "max_rows": None,
                "date_start": None,
                "date_stop": None
            },
            True,
            {
                "params": {
                    "SelectionCriteria": {},
                    "FieldNames": ["AdFormat", "AdGroupId"],
                    "ReportName": "stats_report_2020-03_25",
                    "ReportType": "AD_PERFORMANCE_REPORT",
                    "DateRangeType": "ALL_TIME",
                    "Format": "TSV",
                    "IncludeVAT": "YES"
                }
            }
        ),
        (
            "ALL_TIME",
            {
                "report_language": "en",
                "filters": (),
                "max_rows": None,
                "date_start": None,
                "date_stop": None
            },
            False,
            {
                "params": {
                    "SelectionCriteria": {},
                    "FieldNames": ["AdFormat", "AdGroupId"],
                    "ReportName": "stats_report_2020-03_25",
                    "ReportType": "AD_PERFORMANCE_REPORT",
                    "DateRangeType": "ALL_TIME",
                    "Format": "TSV",
                    "IncludeVAT": "NO"
                }
            }
        ),
        (
            "CUSTOM_DATE",
            {
                "report_language": "en",
                "filters": (),
                "max_rows": 25,
                "date_start": datetime.datetime(2020, 3, 5, 0, 0),
                "date_stop": datetime.datetime(2020, 3, 25, 0, 0)
            },
            False,
            {
                "params": {
                    "SelectionCriteria": {
                        "DateFrom": "2020-03-05",
                        "DateTo": "2020-03-25"
                    },
                    "Page": {
                        "Limit": 25
                    },
                    "FieldNames": ["AdFormat", "AdGroupId"],
                    "ReportName": "stats_report_2020-03_25",
                    "ReportType": "AD_PERFORMANCE_REPORT",
                    "DateRangeType": "CUSTOM_DATE",
                    "Format": "TSV",
                    "IncludeVAT": "NO"
                }
            }
        ),
        (
            "CUSTOM_DATE",
            {
                "report_language": "en",
                "filters": (
                    ("AdGroupId", "EQUALS", ["1"]),
                    ("CampaignId", "IN", ["1", "2"])
                ),
                "max_rows": 25,
                "date_start": datetime.datetime(2020, 3, 5, 0, 0),
                "date_stop": datetime.datetime(2020, 3, 25, 0, 0)
            },
            False,
            {
                "params": {
                    "SelectionCriteria": {
                        "DateFrom": "2020-03-05",
                        "DateTo": "2020-03-25",
                        "Filter": [
                            {
                                "Field": "AdGroupId",
                                "Operator": "EQUALS",
                                "Values": ["1"]
                            },
                            {
                                "Field": "CampaignId",
                                "Operator": "IN",
                                "Values": ["1", "2"]
                            }
                        ]
                    },
                    "Page": {
                        "Limit": 25
                    },
                    "FieldNames": ["AdFormat", "AdGroupId"],
                    "ReportName": "stats_report_2020-03_25",
                    "ReportType": "AD_PERFORMANCE_REPORT",
                    "DateRangeType": "CUSTOM_DATE",
                    "Format": "TSV",
                    "IncludeVAT": "NO"
                }
            }
        )
    ])
    def test_get_query_body(
        self,
        date_range,
        kwargs,
        include_vat,
        expected_query_body
    ):
        reader = YandexStatisticsReader(
            "123",
            ("AdFormat", "AdGroupId"),
            "AD_PERFORMANCE_REPORT",
            "stats_report_2020-03_25",
            date_range,
            include_vat,
            report_language=kwargs["report_language"],
            filters=kwargs["filters"],
            max_rows=kwargs["max_rows"],
            date_start=kwargs["date_start"],
            date_stop=kwargs["date_stop"]
        )
        self.assertDictEqual(reader._build_request_body(), expected_query_body)

    @parameterized.expand(["en", "ru", "uk"])
    def test_request_headers(self, report_language):
        reader = YandexStatisticsReader(
            "123",
            ("AdFormat", "AdGroupId"),
            "AD_PERFORMANCE_REPORT",
            "stats_report_2020-03_25",
            "ALL_TIME",
            True,
            report_language=report_language,
            filters=(),
            max_rows=None,
            date_start=None,
            date_stop=None
        )
        self.assertDictEqual(
            {
                "skipReportSummary": "true",
                "Accept-Language": report_language
            },
            reader._build_request_headers()
        )

    @parameterized.expand([
        (
            "ALL_TIME",
            None,
            None,
            {}
        ),
        (
            "CUSTOM_DATE",
            datetime.datetime(2020, 1, 1),
            datetime.datetime(2020, 1, 2),
            {
                "DateFrom": "2020-01-01",
                "DateTo": "2020-01-02"
            }
        )
    ])
    def test_custom_dates_correctly_set(self, date_range, start_date, stop_date, expected):
        reader = YandexStatisticsReader(
            "123",
            ("AdFormat", "AdGroupId"),
            "AD_PERFORMANCE_REPORT",
            "stats_report_2020-03_25",
            date_range,
            True,
            date_start=start_date,
            date_stop=stop_date
        )
        self.assertDictEqual(
            expected,
            reader._add_custom_dates_if_set()
        )

    @parameterized.expand([
        (
            "ALL_TIME",
            datetime.datetime(2020, 1, 1),
            datetime.datetime(2020, 1, 2),
            "Wrong date range. If start and stop dates are set, should be CUSTOM_DATE."
        ),
        (
            "CUSTOM_DATE",
            None,
            None,
            "Missing at least one date. Have you set start and stop dates?"
        ),
        (
            "CUSTOM_DATE",
            datetime.datetime(2020, 1, 1),
            None,
            "Missing at least one date. Have you set start and stop dates?"
        ),
        (
            "CUSTOM_DATE",
            None,
            datetime.datetime(2020, 1, 1),
            "Missing at least one date. Have you set start and stop dates?"
        ),
        (
            "ALL_TIME",
            None,
            datetime.datetime(2020, 1, 1),
            (
                "Wrong combination of date parameters. "
                "Only use date start and date stop with date range set to CUSTOM_DATE."
            )
        ),
        (
            "ALL_TIME",
            datetime.datetime(2020, 1, 1),
            None,
            (
                "Wrong combination of date parameters. "
                "Only use date start and date stop with date range set to CUSTOM_DATE."
            )
        ),
    ])
    def test_custom_dates_not_correctly_set(
        self,
        date_range,
        start_date,
        stop_date,
        error_message_expected
    ):
        reader = YandexStatisticsReader(
            "123",
            ("AdFormat", "AdGroupId"),
            "AD_PERFORMANCE_REPORT",
            "stats_report_2020-03_25",
            date_range,
            True,
            date_start=start_date,
            date_stop=stop_date
        )
        with self.assertRaises(click.ClickException) as click_exception:
            reader._add_custom_dates_if_set()
        self.assertEquals(click_exception.exception.message, error_message_expected)
