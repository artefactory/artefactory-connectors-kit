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

from nck.clients.api_client import ApiClient
from nck.commands.command import processor
from nck.helpers.yandex_helper import (ATTRIBUTION_MODELS, DATE_RANGE_TYPES,
                                       LANGUAGES, OPERATORS, REPORT_TYPES,
                                       STATS_FIELDS)
from nck.readers.reader import Reader
from nck.streams.json_stream import JSONStream
from nck.utils.args import extract_args


class StrList(click.ParamType):

    def convert(self, value, param, ctx):
        return value.split(",")


STR_LIST_TYPE = StrList()


@click.command(name="read_yandex_statistics")
@click.option("--yandex-token", required=True)
@click.option(
    "--yandex-report-language",
    type=click.Choice(LANGUAGES),
    default="en"
)
@click.option(
    "--yandex-filter",
    "yandex_filters",
    multiple=True,
    type=click.Tuple([click.Choice(STATS_FIELDS), click.Choice(OPERATORS), STR_LIST_TYPE])
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
    type=click.Choice(),
    required=True,
    help=(
        "Fields to output in the report (columns)."
        "For the full list of fields and their meanings, "
        "see https://tech.yandex.com/direct/doc/reports/fields-list-docpage/"
    )
)
@click.option(
    "--yandex-report-name",
    required=True
)
@click.option(
    "--yandex-report-type",
    type=click.Choice(REPORT_TYPES),
    required=True
)
@click.option(
    "--yandex-date-range",
    type=click.Choice(DATE_RANGE_TYPES),
    required=True
)
@click.option(
    "--yandex-include-vat",
    type=click.BOOL,
    required=True,
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
def yandex_statistics(**kwargs):
    return YandexStatisticsReader(**extract_args("yandex_", kwargs))


YANDEX_DIRECT_API_BASE_URL = "https://api.direct.yandex.com/json/v5/"


class YandexStatisticsReader(Reader):

    def __init__(
        self,
        token,
        fields,
        report_type,
        report_name,
        date_range,
        include_vat,
        **kwargs
    ):
        self.token = token
        self.fields = list(fields)
        self.report_type = report_type
        self.report_name = report_name
        self.date_range = date_range
        self.include_vat = include_vat
        self.kwargs = kwargs

    def result_generator(self):
        api_client = ApiClient(self.token, YANDEX_DIRECT_API_BASE_URL)
        request_body = self._build_query_body()
        response = api_client.execute_request(url="reports", body=request_body, headers={})
        yield response.json()

    def _build_request_body(self):
        body = {}
        return body

    def read(self):
        yield JSONStream(
            f"results_{self.report_type}",
            self.result_generator()
        )
