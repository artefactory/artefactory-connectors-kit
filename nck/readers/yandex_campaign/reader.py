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

import nck.helpers.api_client_helper as api_client_helper
from nck.clients.api_client import ApiClient
from nck.readers.reader import Reader
from nck.readers.yandex_campaign.config import YANDEX_DIRECT_API_BASE_URL
from nck.streams.json_stream import JSONStream


class YandexCampaignReader(Reader):
    def __init__(self, token, fields, **kwargs):
        self.token = token
        self.fields = list(fields)
        self.campaign_ids = list(kwargs["campaign_ids"])
        self.campaign_states = list(kwargs["campaign_states"])
        self.campaign_statuses = list(kwargs["campaign_statuses"])
        self.campaign_payment_statuses = list(kwargs["campaign_payment_statuses"])

    def result_generator(self):
        api_client = ApiClient(self.token, YANDEX_DIRECT_API_BASE_URL)
        request_body = self._build_request_body()
        response = api_client.execute_request(url="campaigns", body=request_body, headers={})
        yield response.json()

    def _build_request_body(self):
        body = {}
        body["method"] = "get"
        selection_criteria = {}
        if len(self.campaign_ids) != 0:
            selection_criteria["Ids"] = self.campaign_ids
        if len(self.campaign_states) != 0:
            selection_criteria["States"] = self.campaign_states
        if len(self.campaign_statuses) != 0:
            selection_criteria["Statuses"] = self.campaign_statuses
        if len(self.campaign_payment_statuses) != 0:
            selection_criteria["StatusesPayment"] = self.campaign_payment_statuses
        body["params"] = api_client_helper.get_dict_with_keys_converted_to_new_string_format(
            field_names=self.fields, selection_criteria=selection_criteria
        )
        return body

    def read(self):
        yield JSONStream("results_CAMPAIGN_OBJECT_REPORT_", self.result_generator())
