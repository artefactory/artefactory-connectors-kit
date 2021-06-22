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
from ack.readers.google_dcm.config import REPORT_TYPES
from ack.readers.google_dcm.reader import GoogleDCMReader
from ack.utils.args import extract_args
from ack.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS
from ack.utils.processor import processor


@click.command(name="read_dcm")
@click.option("--dcm-access-token", default=None)
@click.option("--dcm-client-id", required=True)
@click.option("--dcm-client-secret", required=True)
@click.option("--dcm-refresh-token", required=True)
@click.option("--dcm-profile-id", "dcm_profile_ids", required=True, multiple=True)
@click.option("--dcm-report-name", default="DCM Report")
@click.option("--dcm-report-type", type=click.Choice(REPORT_TYPES), default=REPORT_TYPES[0])
@click.option(
    "--dcm-metric",
    "dcm_metrics",
    multiple=True,
    help="https://developers.google.com/doubleclick-advertisers/v3.5/dimensions/#standard-metrics",
)
@click.option(
    "--dcm-dimension",
    "dcm_dimensions",
    multiple=True,
    help="https://developers.google.com/doubleclick-advertisers/v3.5/dimensions/#standard-dimensions",
)
@click.option("--dcm-start-date", type=click.DateTime(), help="Start date of the report")
@click.option("--dcm-end-date", type=click.DateTime(), help="End date of the report")
@click.option(
    "--dcm-filter",
    "dcm_filters",
    type=click.Tuple([str, str]),
    multiple=True,
    help="A filter is a tuple following this pattern: (dimensionName, dimensionValue). "
    "https://developers.google.com/doubleclick-advertisers/v3.5/dimensions/#standard-filters",
)
@click.option(
    "--dcm-date-range",
    type=click.Choice(DEFAULT_DATE_RANGE_FUNCTIONS.keys()),
    help=f"One of the available ACK default date ranges: {DEFAULT_DATE_RANGE_FUNCTIONS.keys()}",
)
@processor("dcm_access_token", "dcm_refresh_token", "dcm_client_secret")
def google_dcm(**kwargs):
    return GoogleDCMReader(**extract_args("dcm_", kwargs))
