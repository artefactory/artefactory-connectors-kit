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

from click import ClickException
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
from nck.readers.facebook_reader import FacebookReader
from parameterized import parameterized


def mock_facebook_obj(data):
    mocked_facebook_obj = mock.MagicMock()
    mocked_facebook_obj._data = data
    return mocked_facebook_obj


class FacebookReaderTest(TestCase):

    DATEFORMAT = "%Y-%m-%d"

    kwargs = {
        "app_id": "",
        "app_secret": "",
        "access_token": "123456789",
        "object_id": ["123456789"],
        "object_type": "account",
        "level": "ad",
        "ad_insights": True,
        "breakdown": [],
        "action_breakdown": [],
        "field": [],
        "time_increment": None,
        "start_date": "2020-01-01",
        "end_date": "2020-02-02",
        "date_preset": None,
        "add_date_to_report": False,
    }

    @parameterized.expand(
        [
            (
                "object_type_and_level_combination",
                {"object_type": "ad", "level": "account"},
            ),
            (
                "ad_insights_level",
                {"ad_insights": True, "object_type": "creative", "level": "creative"},
            ),
            (
                "ad_insights_breakdowns",
                {"ad_insights": True, "field": ["age"], "breakdown": []},
            ),
            (
                "ad_insights_action_breakdowns",
                {
                    "ad_insights": True,
                    "field": ["actions[action_type:link_click]"],
                    "action_breakdown": [],
                },
            ),
            (
                "ad_management_inputs_breakdown_check",
                {"ad_insights": False, "breakdown": ["age"]},
            ),
            (
                "ad_management_inputs_action_breakdown_check",
                {"ad_insights": False, "action_breakdown": ["action_type"]},
            ),
            (
                "ad_management_inputs_time_increment_check",
                {"ad_insights": False, "time_increment": "1"},
            ),
        ]
    )
    @mock.patch.object(FacebookAdsApi, "init", lambda *args: None)
    def test_validate_inputs(self, name, parameters):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update(parameters)
        with self.assertRaises(ClickException):
            FacebookReader(**temp_kwargs)

    @mock.patch.object(FacebookAdsApi, "init", lambda *args: None)
    def test_get_api_fields(self):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update(
            {
                "field": [
                    "impressions",
                    "link_url_asset[website_url]",
                    "actions[action_type:link_click]",
                ],
                "breakdown": ["link_url_asset"],
                "action_breakdown": ["action_type"],
            }
        )
        expected = ["impressions", "actions"]
        self.assertEqual(set(FacebookReader(**temp_kwargs)._api_fields), set(expected))

    @mock.patch.object(FacebookAdsApi, "init", lambda *args: None)
    def test_get_field_paths(self):

        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update(
            {
                "field": [
                    "impressions",
                    "link_url_asset[website_url]",
                    "actions[action_type:link_click]",
                ],
                "breakdown": ["link_url_asset"],
                "action_breakdown": ["action_type"],
            }
        )
        expected = [
            ["impressions"],
            ["link_url_asset", "website_url"],
            ["actions", "action_type:link_click"],
        ]
        self.assertEqual(FacebookReader(**temp_kwargs)._field_paths, expected)

    @mock.patch("nck.readers.facebook_reader.FacebookReader.query_ad_insights")
    @mock.patch.object(FacebookReader, "get_params", lambda *args: {})
    @mock.patch.object(FacebookAdsApi, "init", lambda *args: None)
    def test_read_with_ad_insights_query(self, mock_query_ad_insights):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update({"ad_insights": True, "field": ["date_start", "impressions"]})

        row1, row2 = AdsInsights(), AdsInsights()
        row1.set_data({"date_start": "2020-01-01", "impressions": "1"})
        row2.set_data({"date_start": "2020-01-01", "impressions": "2"})
        mock_query_ad_insights.return_value = [row1, row2]

        data = next(FacebookReader(**temp_kwargs).read())
        expected = [
            {"date_start": "2020-01-01", "impressions": "1"},
            {"date_start": "2020-01-01", "impressions": "2"},
        ]

        for record, report in zip(data.readlines(), iter(expected)):
            self.assertEqual(record, report)

    @mock.patch("nck.readers.facebook_reader.FacebookReader.query_ad_management")
    @mock.patch.object(FacebookReader, "get_params", lambda *args: {})
    @mock.patch.object(FacebookAdsApi, "init", lambda *args: None)
    def test_read_with_ad_management_query(self, mock_query_ad_management):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update({"ad_insights": False, "field": ["id", "status"]})

        row1, row2 = Ad(), Ad()
        row1.set_data({"id": "123456789", "status": "ACTIVE"})
        row2.set_data({"id": "987654321", "status": "PAUSED"})
        mock_query_ad_management.return_value = [row1, row2]

        data = next(FacebookReader(**temp_kwargs).read())
        expected = [
            {"id": "123456789", "status": "ACTIVE"},
            {"id": "987654321", "status": "PAUSED"},
        ]

        for record, report in zip(data.readlines(), iter(expected)):
            self.assertEqual(record, report)

    @parameterized.expand(
        [
            (
                "simple_field",
                {"field": ["impressions"], "action_breakdown": []},
                {"impressions": "10314"},
                {"impressions": "10314"},
            ),
            (
                "nested_field",
                {"field": ["creative[id]"], "action_breakdown": []},
                {"creative": {"id": "123456789"}},
                {"creative[id]": "123456789"},
            ),
            (
                "action_breakdown_field_without_filters",
                {
                    "field": ["actions"],
                    "action_breakdown": ["action_type", "action_device"],
                },
                {
                    "actions": [
                        {"action_type": "link_click", "value": "0"},
                        {"action_type": "post_engagement", "value": "1"},
                    ]
                },
                {
                    "actions[action_type:link_click]": "0",
                    "actions[action_type:post_engagement]": "1",
                },
            ),
            (
                "action_breakdown_field_without_filters",
                {
                    "field": ["actions[action_type:link_click][action_device:iphone]"],
                    "action_breakdown": ["action_type", "action_device"],
                },
                {
                    "actions": [
                        {
                            "action_type": "link_click",
                            "action_device": "iphone",
                            "value": "0",
                        },
                        {
                            "action_type": "post_engagement",
                            "action_device": "iphone",
                            "value": "1",
                        },
                        {
                            "action_type": "link_click",
                            "action_device": "desktop",
                            "value": "2",
                        },
                        {
                            "action_type": "post_engagement",
                            "action_device": "desktop",
                            "value": "3",
                        },
                    ]
                },
                {"actions[action_type:link_click][action_device:iphone]": "0"},
            ),
            (
                "field_not_in_record",
                {"field": ["impressions", "clicks"], "action_breakdown": []},
                {"impressions": "1"},
                {"impressions": "1"},
            ),
            (
                "various_field_formats",
                {"field": ["f_string", "f_numeric", "f_list_of_single_values", "f_python_obj", "f_facebook_obj"]},
                {
                    "f_string": "CAMPAIGN_PAUSED",
                    "f_numeric": 10.95,
                    "f_list_of_single_values": ["CAMPAIGN_PAUSED", 1, 10.95],
                    "f_python_obj": [{"event": "CLICK_THROUGH", "days": 28}, {"event": "VIEW_THROUGH", "days": 1}],
                    "f_facebook_obj": mock_facebook_obj({"id": "123456789", "display_name": "my_object_name"}),
                },
                {
                    "f_string": "CAMPAIGN_PAUSED",
                    "f_numeric": "10.95",
                    "f_list_of_single_values": "CAMPAIGN_PAUSED, 1, 10.95",
                    "f_python_obj": "[{'event': 'CLICK_THROUGH', 'days': 28}, {'event': 'VIEW_THROUGH', 'days': 1}]",
                    "f_facebook_obj": "{'id': '123456789', 'display_name': 'my_object_name'}",
                },
            ),
        ]
    )
    @mock.patch.object(FacebookAdsApi, "init", lambda *args: None)
    def test_format_and_yield(self, name, parameters, record, expected):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update(parameters)
        self.assertEqual(next(FacebookReader(**temp_kwargs).format_and_yield(record)), expected)

    @parameterized.expand(
        [
            ("simple_list_of_dicts", [{"event": "CLICK_THROUGH", "days": 28}, {"event": "VIEW_THROUGH", "days": 1}], False),
            (
                "action_breakdown_list_of_dicts",
                [
                    {"action_type": "link_click", "action_device": "iphone", "value": "0"},
                    {"action_type": "post_engagement", "action_device": "iphone", "value": "1"},
                ],
                True,
            ),
        ]
    )
    def test_obj_follows_action_breakdown_pattern(self, name, obj, expected):
        from nck.helpers.facebook_helper import obj_follows_action_breakdown_pattern

        output = obj_follows_action_breakdown_pattern(obj)
        self.assertEqual(output, expected)

    @parameterized.expand(
        [
            ("list_of_dicts", [{"event": "CLICK_THROUGH", "days": 28}, {"event": "VIEW_THROUGH", "days": 1}], False),
            ("list_of_single_values", ["CAMPAIGN_PAUSED", 1, 10.95], True),
        ]
    )
    def test_obj_is_list_of_single_values(self, name, obj, expected):
        from nck.helpers.facebook_helper import obj_is_list_of_single_values

        output = obj_is_list_of_single_values(obj)
        self.assertEqual(output, expected)
