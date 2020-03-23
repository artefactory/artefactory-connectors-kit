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
import unittest

from nck.readers.yandex_reader import YandexReader


class TestYandexReader(unittest.TestCase):

    def test_get_query_body(self):
        kwargs = {
            "report_language": "en",
            "campaign_id": (),
            "campaign_state": (),
            "campaign_status": (),
            "campaign_payment_allowed": None,
            "filters": (),
            "attribution_model": (),
            "max_rows": None,
            "report_name": None,
            "date_range": None,
            "include_vat": None,
            "date_start": None,
            "date_stop": None
        }
        reader = YandexReader(
            "123",
            ("Id", "Name", "TimeZone", "DailyBudget", "Currency", "EndDate", "StartDate"),
            "CAMPAIGN_OBJECT_REPORT",
            **kwargs
        )

        expected_query_body = {
            "method": "get",
            "params": {
                "SelectionCriteria": {
                },
                "FieldNames": ["Id", "Name", "TimeZone", "DailyBudget", "Currency", "EndDate", "StartDate"]
            }
        }

        self.assertDictEqual(reader._build_query_body(), expected_query_body)
