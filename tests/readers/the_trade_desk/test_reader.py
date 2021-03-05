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
from nck.readers.the_trade_desk.reader import TheTradeDeskReader


class TheTradeDeskReaderTest(TestCase):

    kwargs = {
        "login": "ttd_api_abcde@client.com",
        "password": "XXXXX",
        "advertiser_id": ["advertiser_1", "advertiser_2"],
        "report_template_name": "adgroup_performance_template",
        "report_schedule_name": "adgroup_performance_schedule",
        "start_date": datetime(2020, 1, 1),
        "end_date": datetime(2020, 3, 1),
    }

    @mock.patch("nck.readers.the_trade_desk.reader.TheTradeDeskReader._build_headers", return_value={})
    def test_validate_dates(self, mock_build_headers):
        temp_kwargs = self.kwargs.copy()
        params = {"start_date": datetime(2020, 1, 3), "end_date": datetime(2020, 1, 1)}
        temp_kwargs.update(params)
        with self.assertRaises(ClickException):
            TheTradeDeskReader(**temp_kwargs)

    @mock.patch("nck.readers.the_trade_desk.reader.TheTradeDeskReader._build_headers", return_value={})
    @mock.patch(
        "nck.readers.the_trade_desk.reader.TheTradeDeskReader._make_api_call",
        return_value={
            "Result": [
                {
                    "ReportTemplateId": 1234,
                    "Name": "adgroup_performance_template",
                    "Type": "Custom",
                    "Format": "Text",
                    "CreatedByUserName": "Artefact",
                }
            ],
            "ResultCount": 1,
        },
    )
    def test_get_report_template_id_if_exactly_1_match(self, mock_build_headers, mock_api_call):
        reader = TheTradeDeskReader(**self.kwargs)
        reader._get_report_template_id()
        self.assertEqual(reader.report_template_id, 1234)

    @mock.patch("nck.readers.the_trade_desk.reader.TheTradeDeskReader._build_headers", return_value={})
    @mock.patch(
        "nck.readers.the_trade_desk.reader.TheTradeDeskReader._make_api_call",
        return_value={
            "Result": [
                {
                    "ReportTemplateId": 1234,
                    "Name": "adgroup_performance_template",
                    "Type": "Custom",
                    "Format": "Text",
                    "CreatedByUserName": "Artefact",
                },
                {
                    "ReportTemplateId": 4321,
                    "Name": "adgroup_media_costs_template",
                    "Type": "Custom",
                    "Format": "Text",
                    "CreatedByUserName": "Artefact",
                },
            ],
            "ResultCount": 2,
        },
    )
    def test_get_report_template_id_if_more_than_1_match(self, mock_build_headers, mock_api_call):
        with self.assertRaises(Exception):
            TheTradeDeskReader(**self.kwargs)._get_report_template_id()

    @mock.patch("nck.readers.the_trade_desk.reader.TheTradeDeskReader._build_headers", return_value={})
    @mock.patch(
        "nck.readers.the_trade_desk.reader.TheTradeDeskReader._make_api_call",
        return_value={"Result": [], "ResultCount": 0},
    )
    def test_get_report_template_id_if_no_match(self, mock_build_headers, mock_api_call):
        with self.assertRaises(Exception):
            TheTradeDeskReader(**self.kwargs)._get_report_template_id()

    @mock.patch("nck.readers.the_trade_desk.reader.TheTradeDeskReader._build_headers", return_value={})
    @mock.patch(
        "nck.readers.the_trade_desk.reader.TheTradeDeskReader._make_api_call",
        return_value={
            "ReportScheduleId": 5678,
            "ReportScheduleName": "adgroup_performance_schedule",
        },
    )
    def test_create_report_schedule(self, mock_build_headers, mock_api_call):
        reader = TheTradeDeskReader(**self.kwargs)
        reader.report_template_id = 1234
        reader._create_report_schedule()
        self.assertEqual(reader.report_schedule_id, 5678)

    @mock.patch("nck.readers.the_trade_desk.reader.TheTradeDeskReader._build_headers", return_value={})
    @mock.patch("tenacity.BaseRetrying.wait", side_effect=lambda *args, **kwargs: 0)
    @mock.patch(
        "nck.readers.the_trade_desk.reader.TheTradeDeskReader._make_api_call",
        side_effect=[
            {
                "Result": [
                    {
                        "ReportExecutionId": 8765,
                        "ReportExecutionState": "Pending",
                        "ReportScheduleId": 5678,
                        "ReportScheduleName": "adgroup_performance_schedule",
                        "ReportDeliveries": [{"DownloadURL": None}],
                    }
                ],
                "ResultCount": 1,
            },
            {
                "Result": [
                    {
                        "ReportExecutionId": 8765,
                        "ReportExecutionState": "Completed",
                        "ReportScheduleId": 5678,
                        "ReportScheduleName": "adgroup_performance_schedule",
                        "ReportDeliveries": [{"DownloadURL": "https://download.url"}],
                    }
                ],
                "ResultCount": 1,
            },
        ],
    )
    def test_wait_for_download_url(self, mock_build_headers, mock_retry, mock_api_call):
        reader = TheTradeDeskReader(**self.kwargs)
        reader.report_schedule_id = 5678
        reader._wait_for_download_url()
        self.assertEqual(reader.download_url, "https://download.url")

    @mock.patch("nck.readers.the_trade_desk.reader.TheTradeDeskReader._build_headers", return_value={})
    @mock.patch("tenacity.BaseRetrying.wait", side_effect=lambda *args, **kwargs: 0)
    @mock.patch.object(TheTradeDeskReader, "_get_report_template_id", lambda *args: None)
    @mock.patch.object(TheTradeDeskReader, "_create_report_schedule", lambda *args: None)
    @mock.patch.object(TheTradeDeskReader, "_wait_for_download_url", lambda *args: None)
    @mock.patch(
        "nck.readers.the_trade_desk.reader.TheTradeDeskReader._download_report",
        return_value=iter(
            [
                {"Date": "2020-01-01T00:00:00", "Advertiser ID": "XXXXX", "Impressions": 10},
                {"Date": "2020-02-01T00:00:00", "Advertiser ID": "XXXXX", "Impressions": 11},
                {"Date": "2020-02-03T00:00:00", "Advertiser ID": "XXXXX", "Impressions": 12},
            ]
        ),
    )
    def test_read(self, mock_build_headers, mock_retry, mock_download_report):
        reader = TheTradeDeskReader(**self.kwargs)
        reader.report_template_id = 1234
        reader.report_schedule_id = 5678
        reader.download_url = "https://download.url"
        output = next(reader.read())
        expected = [
            {"Date": "2020-01-01", "Advertiser ID": "XXXXX", "Impressions": 10},
            {"Date": "2020-02-01", "Advertiser ID": "XXXXX", "Impressions": 11},
            {"Date": "2020-02-03", "Advertiser ID": "XXXXX", "Impressions": 12},
        ]
        for output_record, expected_record in zip(output.readlines(), iter(expected)):
            self.assertEqual(output_record, expected_record)
