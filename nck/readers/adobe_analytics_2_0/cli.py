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
from nck.readers.adobe_analytics_2_0.reader import AdobeAnalytics20Reader
from nck.utils.args import extract_args
from nck.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS


def format_key_if_needed(ctx, param, value):
    """
    In some cases, newlines are escaped when passed as a click.option().
    This callback corrects this unexpected behaviour.
    """
    return value.replace("\\n", "\n")


@click.command(name="read_adobe_2_0")
@click.option(
    "--adobe-2-0-client-id",
    required=True,
    help="Client ID, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-2-0-client-secret",
    required=True,
    help="Client Secret, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-2-0-tech-account-id",
    required=True,
    help="Technical Account ID, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-2-0-org-id",
    required=True,
    help="Organization ID, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-2-0-private-key",
    required=True,
    callback=format_key_if_needed,
    help="Content of the private.key file, that you had to provide to create the integration. "
    "Make sure to enter the parameter in quotes, include headers, and indicate newlines as '\\n'.",
)
@click.option(
    "--adobe-2-0-global-company-id",
    required=True,
    help="Global Company ID, to be requested to Discovery API. "
    "Doc: https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/discovery.md)",
)
@click.option(
    "--adobe-2-0-report-suite-id",
    required=True,
    help="ID of the requested Adobe Report Suite",
)
@click.option(
    "--adobe-2-0-dimension",
    required=True,
    multiple=True,
    help="To get dimension names, enable the Debugger feature in Adobe Analytics Workspace: "
    "it will allow you to visualize the back-end JSON requests made by Adobe Analytics UI to Reporting API 2.0. "
    "Doc: https://github.com/AdobeDocs/analytics-2.0-apis/blob/master/reporting-tricks.md",
)
@click.option(
    "--adobe-2-0-metric",
    required=True,
    multiple=True,
    help="To get metric names, enable the Debugger feature in Adobe Analytics Workspace: "
    "it will allow you to visualize the back-end JSON requests made by Adobe Analytics UI to Reporting API 2.0. "
    "Doc: https://github.com/AdobeDocs/analytics-2.0-apis/blob/master/reporting-tricks.md",
)
@click.option(
    "--adobe-2-0-start-date",
    type=click.DateTime(),
    help="Start date of the report",
)
@click.option(
    "--adobe-2-0-end-date",
    type=click.DateTime(),
    help="End date of the report",
)
@click.option(
    "--adobe-2-0-date-range",
    type=click.Choice(DEFAULT_DATE_RANGE_FUNCTIONS.keys()),
    help=f"One of the available NCK default date ranges: {DEFAULT_DATE_RANGE_FUNCTIONS.keys()}",
)
@processor(
    "adobe_2_0_client_id",
    "adobe_2_0_client_secret",
    "adobe_2_0_tech_account_id",
    "adobe_2_0_org_id",
    "adobe_2_0_private_key",
)
def adobe_analytics_2_0(**kwargs):
    return AdobeAnalytics20Reader(**extract_args("adobe_2_0_", kwargs))
