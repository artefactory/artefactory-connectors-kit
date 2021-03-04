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
from unittest import TestCase, mock

from nck.readers.adobe_analytics_2_0.reader import AdobeAnalytics20Reader


class AdobeReaderTest_2_0(TestCase):

    kwargs = {
        "client_id": "",
        "client_secret": "",
        "tech_account_id": "",
        "org_id": "",
        "private_key": "",
        "global_company_id": "",
        "report_suite_id": "XXXXXXXXX",
        "dimension": [],
        "metric": [],
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2020, 1, 2),
        "date_range": None,
    }

    @mock.patch("nck.clients.adobe_analytics.client.AdobeAnalyticsClient.__init__", return_value=None)
    def test_build_date_range(self, mock_adobe_client):
        output = AdobeAnalytics20Reader(**self.kwargs).build_date_range()
        expected = "2020-01-01T00:00:00/2020-01-03T00:00:00"
        self.assertEqual(output, expected)

    @mock.patch("nck.clients.adobe_analytics.client.AdobeAnalyticsClient.__init__", return_value=None)
    def test_build_report_description_one_dimension(self, mock_adobe_client):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update({"dimension": ["daterangeday"]})
        metrics = ["visits", "bounces"]

        output = AdobeAnalytics20Reader(**temp_kwargs).build_report_description(metrics)
        expected = {
            "rsid": "XXXXXXXXX",
            "globalFilters": [
                {
                    "type": "dateRange",
                    "dateRange": "2020-01-01T00:00:00/2020-01-03T00:00:00",
                }
            ],
            "metricContainer": {
                "metricFilters": [],
                "metrics": [
                    {"id": "metrics/visits", "filters": []},
                    {"id": "metrics/bounces", "filters": []},
                ],
            },
            "dimension": "variables/daterangeday",
            "settings": {"countRepeatInstances": "true", "limit": "5000"},
        }
        self.assertEqual(output, expected)

    @mock.patch("nck.clients.adobe_analytics.client.AdobeAnalyticsClient.__init__", return_value=None)
    def test_build_report_description_multiple_dimensions(self, mock_adobe_client):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update({"dimension": ["daterangeday", "campaign", "pagename"]})
        metrics = ["visits", "bounces"]
        breakdown_item_ids = ["000000000", "111111111"]

        output = AdobeAnalytics20Reader(**temp_kwargs).build_report_description(metrics, breakdown_item_ids)
        expected = {
            "rsid": "XXXXXXXXX",
            "globalFilters": [
                {
                    "type": "dateRange",
                    "dateRange": "2020-01-01T00:00:00/2020-01-03T00:00:00",
                }
            ],
            "metricContainer": {
                "metricFilters": [
                    {
                        "id": 0,
                        "type": "breakdown",
                        "dimension": "variables/daterangeday",
                        "itemId": "000000000",
                    },
                    {
                        "id": 1,
                        "type": "breakdown",
                        "dimension": "variables/campaign",
                        "itemId": "111111111",
                    },
                    {
                        "id": 2,
                        "type": "breakdown",
                        "dimension": "variables/daterangeday",
                        "itemId": "000000000",
                    },
                    {
                        "id": 3,
                        "type": "breakdown",
                        "dimension": "variables/campaign",
                        "itemId": "111111111",
                    },
                ],
                "metrics": [
                    {"id": "metrics/visits", "filters": [0, 1]},
                    {"id": "metrics/bounces", "filters": [2, 3]},
                ],
            },
            "dimension": "variables/pagename",
            "settings": {"countRepeatInstances": "true", "limit": "5000"},
        }
        self.assertEqual(output, expected)

    @mock.patch("nck.clients.adobe_analytics.client.AdobeAnalyticsClient.__init__", return_value=None)
    @mock.patch(
        "nck.readers.adobe_analytics_2_0.reader.AdobeAnalytics20Reader.get_report_page",
        side_effect=[
            {
                "totalPages": 2,
                "firstPage": True,
                "lastPage": False,
                "columns": {"dimension": {"id": "variables/daterangeday"}},
                "rows": [
                    {"itemId": "1200201", "value": "Jan 1, 2020", "data": [11, 21]},
                    {"itemId": "1200202", "value": "Jan 2, 2020", "data": [12, 22]},
                ],
            },
            {
                "totalPages": 2,
                "firstPage": False,
                "lastPage": True,
                "columns": {"dimension": {"id": "variables/daterangeday"}},
                "rows": [
                    {"itemId": "1200203", "value": "Jan 3, 2020", "data": [13, 23]},
                    {"itemId": "1200204", "value": "Jan 4, 2020", "data": [14, 24]},
                ],
            },
        ],
    )
    def test_get_parsed_report(self, mock_adobe_client, mock_get_report_page):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update(
            {
                "dimension": ["daterangeday"],
                "start_date": datetime.date(2020, 1, 1),
                "end_date": datetime.date(2020, 1, 4),
            }
        )
        metrics = ["visits", "bounces"]

        output = AdobeAnalytics20Reader(**temp_kwargs).get_parsed_report({"dimension": "variables/daterangeday"}, metrics)
        expected = [
            {"daterangeday": "2020-01-01", "visits": 11, "bounces": 21},
            {"daterangeday": "2020-01-02", "visits": 12, "bounces": 22},
            {"daterangeday": "2020-01-03", "visits": 13, "bounces": 23},
            {"daterangeday": "2020-01-04", "visits": 14, "bounces": 24},
        ]
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)

    @mock.patch("nck.clients.adobe_analytics.client.AdobeAnalyticsClient.__init__", return_value=None)
    @mock.patch(
        "nck.readers.adobe_analytics_2_0.reader.AdobeAnalytics20Reader.get_node_values",
        return_value={
            "lasttouchchannel_1": "Paid Search",
            "lasttouchchannel_2": "Natural_Search",
        },
    )
    def test_add_child_nodes_to_graph(self, mock_adobe_client, mock_get_node_values):
        graph = {
            "root": ["daterangeday_1200201", "daterangeday_1200202"],
            "daterangeday_1200201": [],
            "daterangeday_1200202": [],
        }
        node = "daterangeday_1200201"
        path_to_node = ["daterangeday_1200201"]

        output = AdobeAnalytics20Reader(**self.kwargs).add_child_nodes_to_graph(graph, node, path_to_node)
        expected = {
            "root": ["daterangeday_1200201", "daterangeday_1200202"],
            "daterangeday_1200201": ["lasttouchchannel_1", "lasttouchchannel_2"],
            "daterangeday_1200202": [],
            "lasttouchchannel_1": [],
            "lasttouchchannel_2": [],
        }
        self.assertEqual(output, expected)

    @mock.patch("nck.clients.adobe_analytics.client.AdobeAnalyticsClient.__init__", return_value=None)
    @mock.patch(
        "nck.readers.adobe_analytics_2_0.reader.AdobeAnalytics20Reader.get_parsed_report",
        return_value=[
            {"daterangeday": "2020-01-01", "visits": 11, "bounces": 21},
            {"daterangeday": "2020-01-02", "visits": 12, "bounces": 22},
        ],
    )
    def test_read_one_dimension_reports(self, mock_adobe_client, mock_get_parsed_report):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update({"dimension": ["daterangeday"], "metric": ["visits", "bounces"]})

        output = next(AdobeAnalytics20Reader(**temp_kwargs).read())
        expected = [
            {"daterangeday": "2020-01-01", "visits": 11, "bounces": 21},
            {"daterangeday": "2020-01-02", "visits": 12, "bounces": 22},
        ]
        for output_record, expected_output in zip(output.readlines(), iter(expected)):
            self.assertEqual(output_record, expected_output)

    @mock.patch("nck.clients.adobe_analytics.client.AdobeAnalyticsClient.__init__", return_value=None)
    @mock.patch(
        "nck.readers.adobe_analytics_2_0.reader.AdobeAnalytics20Reader.add_child_nodes_to_graph",
        side_effect=[
            {
                "root": ["daterangeday_1200201", "daterangeday_1200202"],
                "daterangeday_1200201": [],
                "daterangeday_1200202": [],
            },
            {
                "root": ["daterangeday_1200201", "daterangeday_1200202"],
                "daterangeday_1200201": ["lasttouchchannel_1"],
                "daterangeday_1200202": [],
                "lasttouchchannel_1": [],
            },
            {
                "root": ["daterangeday_1200201", "daterangeday_1200202"],
                "daterangeday_1200201": ["lasttouchchannel_1"],
                "daterangeday_1200202": ["lasttouchchannel_2"],
                "lasttouchchannel_1": [],
                "lasttouchchannel_2": [],
            },
        ],
    )
    @mock.patch(
        "nck.readers.adobe_analytics_2_0.reader.AdobeAnalytics20Reader.get_parsed_report",
        side_effect=[
            [
                {
                    "daterangeday": "2020-01-01",
                    "lastouchchannel": "Paid Search",
                    "campaign": "Campaign_1",
                    "visits": 11,
                    "bounces": 21,
                },
                {
                    "daterangeday": "2020-01-01",
                    "lastouchchannel": "Paid Search",
                    "campaign": "Campaign_2",
                    "visits": 12,
                    "bounces": 22,
                },
            ],
            [
                {
                    "daterangeday": "2020-01-02",
                    "lastouchchannel": "Natural Search",
                    "campaign": "Campaign_1",
                    "visits": 13,
                    "bounces": 23,
                },
                {
                    "daterangeday": "2020-01-02",
                    "lastouchchannel": "Natural Search",
                    "campaign": "Campaign_2",
                    "visits": 14,
                    "bounces": 24,
                },
            ],
        ],
    )
    def test_read_multiple_dimension_reports(self, mock_adobe_client, mock_add_child_nodes_to_graph, mock_get_parsed_report):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update(
            {
                "dimension": ["daterangeday", "lastouchchannel", "campaign"],
                "metric": ["visits", "bounces"],
            }
        )
        reader = AdobeAnalytics20Reader(**temp_kwargs)
        reader.node_values = {
            "daterangeday_1200201": "Jan 1, 2020",
            "daterangeday_1200202": "Jan 2, 2020",
            "lasttouchchannel_1": "Paid Search",
            "lasttouchchannel_2": "Natural Search",
        }
        output = next(reader.read())
        expected = [
            {
                "daterangeday": "2020-01-01",
                "lastouchchannel": "Paid Search",
                "campaign": "Campaign_1",
                "visits": 11,
                "bounces": 21,
            },
            {
                "daterangeday": "2020-01-01",
                "lastouchchannel": "Paid Search",
                "campaign": "Campaign_2",
                "visits": 12,
                "bounces": 22,
            },
            {
                "daterangeday": "2020-01-02",
                "lastouchchannel": "Natural Search",
                "campaign": "Campaign_1",
                "visits": 13,
                "bounces": 23,
            },
            {
                "daterangeday": "2020-01-02",
                "lastouchchannel": "Natural Search",
                "campaign": "Campaign_2",
                "visits": 14,
                "bounces": 24,
            },
        ]
        for output_record, expected_record in zip(output.readlines(), iter(expected)):
            self.assertEqual(output_record, expected_record)
