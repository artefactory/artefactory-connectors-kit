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
from nck.readers.google_sa360.config import REPORT_TYPES
from nck.readers.google_sa360.reader import GoogleSA360Reader
from nck.utils.args import extract_args


@click.command(name="read_sa360")
@click.option("--sa360-access-token", default=None)
@click.option("--sa360-client-id", required=True)
@click.option("--sa360-client-secret", required=True)
@click.option("--sa360-refresh-token", required=True)
@click.option("--sa360-agency-id", required=True)
@click.option(
    "--sa360-advertiser-id",
    "sa360_advertiser_ids",
    multiple=True,
    help="If empty, all advertisers from agency will be requested",
)
@click.option("--sa360-report-name", default="SA360 Report")
@click.option("--sa360-report-type", type=click.Choice(REPORT_TYPES), default=REPORT_TYPES[0])
@click.option(
    "--sa360-column",
    "sa360_columns",
    multiple=True,
    help="https://developers.google.com/search-ads/v2/report-types",
)
@click.option(
    "--sa360-saved-column",
    "sa360_saved_columns",
    multiple=True,
    help="https://developers.google.com/search-ads/v2/how-tos/reporting/saved-columns",
)
@click.option("--sa360-start-date", type=click.DateTime(), required=True)
@click.option("--sa360-end-date", type=click.DateTime(), required=True)
@processor("sa360_access_token", "sa360_refresh_token", "sa360_client_secret")
def google_sa360(**kwargs):
    return GoogleSA360Reader(**extract_args("sa360_", kwargs))
