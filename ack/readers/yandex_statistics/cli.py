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
import random

import click
from ack.readers.yandex_statistics.config import DATE_RANGE_TYPES, LANGUAGES, OPERATORS, REPORT_TYPES, STATS_FIELDS
from ack.readers.yandex_statistics.reader import YandexStatisticsReader
from ack.utils.args import extract_args
from ack.utils.processor import processor


class StrList(click.ParamType):
    def convert(self, value, param, ctx):
        return value.split(",")


STR_LIST_TYPE = StrList()


@click.command(name="read_yandex_statistics")
@click.option("--yandex-statistics-token", "yandex_token", required=True)
@click.option("--yandex-statistics-report-language", "yandex_report_language", type=click.Choice(LANGUAGES), default="en")
@click.option(
    "--yandex-statistics-filter",
    "yandex_filters",
    multiple=True,
    type=click.Tuple([click.Choice(STATS_FIELDS), click.Choice(OPERATORS), STR_LIST_TYPE]),
)
@click.option("--yandex-statistics-max-rows", "yandex_max_rows", type=int)
@click.option(
    "--yandex-statistics-field-name",
    "yandex_fields",
    multiple=True,
    type=click.Choice(STATS_FIELDS),
    required=True,
    help=(
        "Fields to output in the report (columns)."
        "For the full list of fields and their meanings, "
        "see https://tech.yandex.com/direct/doc/reports/fields-list-docpage/"
    ),
)
@click.option(
    "--yandex-statistics-report-name",
    "yandex_report_name",
    default=f"stats_report_{datetime.date.today()}_{random.randrange(10000)}",
)
@click.option("--yandex-statistics-report-type", "yandex_report_type", type=click.Choice(REPORT_TYPES), required=True)
@click.option("--yandex-statistics-date-range", "yandex_date_range", type=click.Choice(DATE_RANGE_TYPES), required=True)
@click.option(
    "--yandex-statistics-include-vat",
    "yandex_include_vat",
    type=click.BOOL,
    required=True,
    help="Whether to include VAT in the monetary amounts in the report.",
)
@click.option("--yandex-statistics-date-start", "yandex_date_start", type=click.DateTime())
@click.option("--yandex-statistics-date-stop", "yandex_date_stop", type=click.DateTime())
@processor("yandex_token")
def yandex_statistics(**kwargs):
    return YandexStatisticsReader(**extract_args("yandex_", kwargs))
