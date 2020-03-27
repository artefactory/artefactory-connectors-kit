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
from unittest import TestCase

from nck.clients.api_client import ApiClient


class ApiClientTest(TestCase):

    def test_get_formatted_request_body(self):
        selection_criteria = {
            "Filter": [
                {
                    "Field": "CampaignId",
                    "Operator": "IN",
                    "Values": ["123", "456"]
                }
            ]
        }
        page = {
            "Limit": 10
        }
        field_names = ["AdGroupId", "Year", "CampaignName"]
        report_name = "test"
        report_type = "CAMPAIGN_PERFORMANCE_REPORT"
        date_range_type = "ALL_TIME"
        include_vat = "NO"

        expected_output = {
            "SelectionCriteria": selection_criteria,
            "Page": page,
            "FieldNames": field_names,
            "ReportName": report_name,
            "ReportType": report_type,
            "DateRangeType": date_range_type,
            "IncludeVAT": include_vat
        }
        self.assertDictEqual(
            ApiClient.get_formatted_request_body(
                selection_criteria=selection_criteria,
                page=page,
                field_names=field_names,
                report_name=report_name,
                report_type=report_type,
                date_range_type=date_range_type,
                include_v_a_t=include_vat
            ),
            expected_output
        )
