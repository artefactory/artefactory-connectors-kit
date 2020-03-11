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
    DATE_RANGE_TYPES, OPERATORS
)


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
    default=False,
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


class YandexReader(Reader):
    def __init__(
        self,
        token,
        report_language,
        filters,
        attribution_model,
        max_rows,
        fields,
        report_name,
        report_type,
        date_range,
        include_vat,
        date_start,
        date_stop
    ):
        self.token = token
        self.report_language = report_language
        self.filters = filters
        self.attribution_model = attribution_model
        self.max_rows = max_rows
        self.fields = fields
        self.report_name = report_name
        self.report_type = report_type
        self.date_range = date_range
        self.include_vat = include_vat
        self.date_start = date_start
        self.date_stop = date_stop
