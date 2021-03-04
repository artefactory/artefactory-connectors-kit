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
from nck.readers.google_ads.config import DATE_RANGE_TYPE_POSSIBLE_VALUES, REPORT_TYPE_POSSIBLE_VALUES
from nck.readers.google_ads.reader import GoogleAdsReader
from nck.utils.args import extract_args


@click.command(name="read_googleads")
@click.option("--googleads-developer-token", required=True)
@click.option("--googleads-client-id", required=True)
@click.option("--googleads-client-secret", required=True)
@click.option("--googleads-refresh-token", required=True)
@click.option(
    "--googleads-manager-id",
    help="Google Ads Manager Account. " "Optional: can be used to get the reports from all accounts in hierarchy",
)
@click.option(
    "--googleads-client-customer-id",
    "googleads_client_customer_ids",
    multiple=True,
    help="Google Ads Client Account(s) to be called, thanks to their IDs.\n "
    "This field is ignored if manager_id is specified (replaced by the accounts linked to the MCC)",
)
@click.option("--googleads-report-name", default="CustomReport", help="Name given to your Report")
@click.option(
    "--googleads-report-type",
    type=click.Choice(REPORT_TYPE_POSSIBLE_VALUES),
    default=REPORT_TYPE_POSSIBLE_VALUES[0],
    help="Desired Report Type to fetch\n" "https://developers.google.com/adwords/api/docs/appendix/reports#available-reports",
)
@click.option(
    "--googleads-date-range-type",
    type=click.Choice(DATE_RANGE_TYPE_POSSIBLE_VALUES),
    help="Desired Date Range Type to fetch\n" "https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges",
)
@click.option("--googleads-start-date", type=click.DateTime())
@click.option("--googleads-end-date", type=click.DateTime())
@click.option(
    "--googleads-field",
    "googleads_fields",
    multiple=True,
    help="Google Ads API fields for the request\n"
    "https://developers.google.com/adwords/api/docs/appendix/reports#available-reports",
)
@click.option(
    "--googleads-report-filter",
    default="{}",
    help="A filter can be applied on a chosen field, "
    "in the form of a String containing a Dictionary \"{'field','operator','values'}\"\n"
    "https://developers.google.com/adwords/api/docs/guides/reporting#create_a_report_definition",
)
@click.option(
    "--googleads-include-zero-impressions",
    default=True,
    type=click.BOOL,
    help="A boolean indicating whether the report should show rows with zero impressions",
)
@click.option(
    "--googleads-filter-on-video-campaigns",
    default=False,
    type=click.BOOL,
    help="A boolean indicating whether the report should return only Video campaigns\n"
    "Only available if CampaignId is requested as a report field",
)
@click.option(
    "--googleads-include-client-customer-id",
    default=False,
    type=click.BOOL,
    help="A boolean indicating whether the Account ID should be included as a field in the output stream\n"
    "(because AccountId is not available as a report field in the API)",
)
@processor("googleads_developer_token", "googleads_app_secret", "googleads_refresh_token")
def google_ads(**kwargs):
    return GoogleAdsReader(**extract_args("googleads_", kwargs))
