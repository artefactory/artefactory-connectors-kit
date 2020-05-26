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
import click

import nck.helpers.api_client_helper as api_client_helper
from nck.clients.api_client import ApiClient
from nck.commands.command import processor
from nck.helpers.yandex_helper import (CAMPAIGN_FIELDS, CAMPAIGN_STATES,
                                       CAMPAIGN_STATUSES, CAMPAIGN_PAYMENT_STATUSES)
from nck.readers.reader import Reader
from nck.streams.json_stream import JSONStream
from nck.utils.args import extract_args


@click.command(name="read_yandex_campaigns")
@click.option("--yandex-token", required=True)
@click.option(
    "--yandex-campaign-id",
    "yandex_campaign_ids",
    multiple=True
)
@click.option(
    "--yandex-campaign-state",
    "yandex_campaign_states",
    multiple=True,
    type=click.Choice(CAMPAIGN_STATES)
)
@click.option(
    "--yandex-campaign-status",
    "yandex_campaign_statuses",
    multiple=True,
    type=click.Choice(CAMPAIGN_STATUSES)
)
@click.option(
    "--yandex-campaign-payment-status",
    "yandex_campaign_payment_statuses",
    multiple=True,
    type=click.Choice(CAMPAIGN_PAYMENT_STATUSES)
)
@click.option(
    "--yandex-field-name",
    "yandex_fields",
    multiple=True,
    type=click.Choice(CAMPAIGN_FIELDS),
    required=True,
    help=(
        "Fields to output in the report (columns)."
        "For the full list of fields and their meanings, "
        "see https://tech.yandex.com/direct/doc/reports/fields-list-docpage/"
    )
)
@processor("yandex_token")
def yandex_campaigns(**kwargs):
    return YandexCampaignReader(**extract_args("yandex_", kwargs))


YANDEX_DIRECT_API_BASE_URL = "https://api.direct.yandex.com/json/v5/"


class YandexCampaignReader(Reader):

    def __init__(
        self,
        token,
        fields,
        **kwargs
    ):
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
            field_names=self.fields,
            selection_criteria=selection_criteria
        )
        return body

    def read(self):
        yield JSONStream(
            "results_CAMPAIGN_OBJECT_REPORT_",
            self.result_generator()
        )
