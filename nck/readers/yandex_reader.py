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

from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.utils.args import extract_args
from nck.helpers.yandex_helper import (
    LANGUAGES, REPORT_TYPES, FIELDS, ATTRIBUTION_MODELS,
    DATE_RANGE_TYPES, OPERATORS, CAMPAIGN_STATES, CAMPAIGN_STATUSES
)
from nck.clients.api_client import ApiClient
from nck.streams.json_stream import JSONStream


class StrList(click.ParamType):

    def convert(self, value, param, ctx):
        return value.split(",")


STR_LIST_TYPE = StrList()


@click.command(name="read_yandex")
@click.option("--yandex-token", required=True)
@click.option(
    "--yandex-report-language",
    type=click.Choice(LANGUAGES),
    default="en"
)
@click.option(
    "--yandex-campaign-id",
    multiple=True
)
@click.option(
    "--yandex-campaign-state",
    multiple=True,
    type=click.Choice(CAMPAIGN_STATES)
)
@click.option(
    "--yandex-campaign-status",
    multiple=True,
    type=click.Choice(CAMPAIGN_STATUSES)
)
@click.option(
    "--yandex-campaign-payment-allowed",
    type=click.BOOL
)
@click.option(
    "--yandex-filter",
    "yandex_filters",
    multiple=True,
    type=click.Tuple([click.Choice(FIELDS), click.Choice(OPERATORS), STR_LIST_TYPE])
)
@click.option(
    "--yandex-attribution-model",
    multiple=True,
    type=click.Choice(ATTRIBUTION_MODELS)
)
@click.option(
    "--yandex-max-rows",
    type=int
)
@click.option(
    "--yandex-field-name",
    "yandex_fields",
    multiple=True,
    type=click.Choice(FIELDS),
    required=True,
    help=(
        "Fields to output in the report (columns)."
        "For the full list of fields and their meanings, "
        "see https://tech.yandex.com/direct/doc/reports/fields-list-docpage/"
    )
)
@click.option(
    "--yandex-report-name"
)
@click.option(
    "--yandex-report-type",
    type=click.Choice(REPORT_TYPES),
    required=True
)
@click.option(
    "--yandex-date-range",
    type=click.Choice(DATE_RANGE_TYPES)
)
@click.option(
    "--yandex-include-vat",
    type=click.BOOL,
    help="Whether to include VAT in the monetary amounts in the report."
)
@click.option(
    "--yandex-date-start",
    type=click.DateTime()
)
@click.option(
    "--yandex-date-stop",
    type=click.DateTime()
)
@processor("yandex_token")
def yandex(**kwargs):
    return YandexReader(**extract_args("yandex_", kwargs))


YANDEX_DIRECT_API_BASE_URL = "https://api.direct.yandex.com/json/v5/"


class YandexReader(Reader):

    def __init__(
        self,
        token,
        fields,
        report_type,
        **kwargs
    ):
        self.token = token
        self.fields = fields
        self.report_type = report_type
        self.kwargs = kwargs

    def result_generator(self):
        api_client = ApiClient(self.token, YANDEX_DIRECT_API_BASE_URL)
        request_body = self._build_query_body()
        response = api_client.execute_request(url="campaigns", body=request_body, headers={})
        yield response.json()

    def _build_query_body(self):
        body = {}
        if self.report_type == "CAMPAIGN_OBJECT_REPORT":
            body["method"] = "get"
            body["params"] = ApiClient.get_formatted_request_body(
                field_names=self.fields,
                selection_criteria={}
            )
        return body

    def read(self):
        yield JSONStream(
            f"results_{self.report_type}",
            self.result_generator()
        )
