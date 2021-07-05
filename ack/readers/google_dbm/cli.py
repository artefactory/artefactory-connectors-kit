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
from ack.readers.google_dbm.config import POSSIBLE_REQUEST_TYPES, POSSIBLE_FREQUENCIES, POSSIBLE_TIMEZONE_CODES
from ack.readers.google_dbm.reader import GoogleDBMReader
from ack.utils.args import extract_args
from ack.utils.processor import processor


@click.command(name="read_dbm")
@click.option("--dbm-access-token", default=None)
@click.option("--dbm-refresh-token", required=True)
@click.option("--dbm-client-id", required=True)
@click.option("--dbm-client-secret", required=True)
@click.option("--dbm-query-metric", multiple=True)
@click.option("--dbm-query-dimension", multiple=True)
@click.option("--dbm-request-type", type=click.Choice(POSSIBLE_REQUEST_TYPES), required=True)
@click.option("--dbm-query-id")
@click.option("--dbm-query-title")
@click.option("--dbm-query-frequency", type=click.Choice(POSSIBLE_FREQUENCIES), default="ONE_TIME")
@click.option("--dbm-query-timezone-code", type=click.Choice(POSSIBLE_TIMEZONE_CODES), default="America/New_York")
@click.option("--dbm-query-param-type", default="TYPE_TRUEVIEW")
@click.option("--dbm-start-date", type=click.DateTime())
@click.option("--dbm-end-date", type=click.DateTime())
@click.option(
    "--dbm-add-date-to-report",
    type=click.BOOL,
    default=False,
    help=(
        "Sometimes the date range on which metrics are computed is missing from the report. "
        "If this option is set to True, this range will be added."
    ),
)
@click.option("--dbm-filter", type=click.Tuple([str, str]), multiple=True)
@click.option("--dbm-file-type", multiple=True)
@click.option(
    "--dbm-date-format",
    default="%Y-%m-%d",
    help="Add optional date format for the output stream. "
    "Follow the syntax of https://docs.python.org/3.8/library/datetime.html#strftime-strptime-behavior",
)
@click.option(
    "--dbm-day-range",
    type=click.Choice(["PREVIOUS_DAY", "LAST_30_DAYS", "LAST_90_DAYS", "LAST_7_DAYS", "PREVIOUS_MONTH", "PREVIOUS_WEEK"]),
)
@processor("dbm_access_token", "dbm_refresh_token", "dbm_client_secret")
def google_dbm(**kwargs):
    # Should add validation argument in function of request_type
    return GoogleDBMReader(**extract_args("dbm_", kwargs))
