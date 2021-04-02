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
from ack.readers.the_trade_desk.reader import TheTradeDeskReader
from ack.utils.args import extract_args
from ack.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS
from ack.utils.processor import processor


@click.command(name="read_ttd")
@click.option("--ttd-login", required=True, help="Login of your API account")
@click.option("--ttd-password", required=True, help="Password of your API account")
@click.option(
    "--ttd-advertiser-id", required=True, multiple=True, help="Advertiser Ids for which report data should be fetched",
)
@click.option(
    "--ttd-report-template-name",
    required=True,
    help="Exact name of the Report Template to request. Existing Report Templates "
    "can be found within the MyReports section of The Trade Desk UI.",
)
@click.option(
    "--ttd-report-schedule-name", required=True, help="Name of the Report Schedule to create.",
)
@click.option(
    "--ttd-start-date", type=click.DateTime(), help="Start date of the period to request (format: YYYY-MM-DD)",
)
@click.option(
    "--ttd-end-date", type=click.DateTime(), help="End date of the period to request (format: YYYY-MM-DD)",
)
@click.option(
    "--ttd-date-range",
    type=click.Choice(DEFAULT_DATE_RANGE_FUNCTIONS.keys()),
    help=f"One of the available ACK default date ranges: {DEFAULT_DATE_RANGE_FUNCTIONS.keys()}",
)
@processor("ttd_login", "ttd_password")
def the_trade_desk(**kwargs):
    return TheTradeDeskReader(**extract_args("ttd_", kwargs))
