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
from nck.readers.adobe_analytics_1_4.reader import AdobeAnalytics14Reader
from nck.utils.args import extract_args


def format_key_if_needed(ctx, param, value):
    """
    In some cases, newlines are escaped when passed as a click.option().
    This callback corrects this unexpected behaviour.
    """
    return value.replace("\\n", "\n")


@click.command(name="read_adobe")
@click.option(
    "--adobe-client-id",
    required=True,
    help="Client ID, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-client-secret",
    required=True,
    help="Client Secret, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-tech-account-id",
    required=True,
    help="Technical Account ID, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-org-id",
    required=True,
    help="Organization ID, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-private-key",
    required=True,
    callback=format_key_if_needed,
    help="Content of the private.key file, that you had to provide to create the integration. "
    "Make sure to enter the parameter in quotes, include headers, and indicate newlines as '\\n'.",
)
@click.option(
    "--adobe-global-company-id",
    required=True,
    help="Global Company ID, to be requested to Discovery API. "
    "Doc: https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/discovery.md)",
)
@click.option("--adobe-list-report-suite", type=click.BOOL, default=False)
@click.option("--adobe-report-suite-id")
@click.option("--adobe-report-element-id", multiple=True)
@click.option("--adobe-report-metric-id", multiple=True)
@click.option("--adobe-date-granularity", default=None)
@click.option(
    "--adobe-day-range",
    type=click.Choice(["PREVIOUS_DAY", "LAST_30_DAYS", "LAST_7_DAYS", "LAST_90_DAYS"]),
    default=None,
)
@click.option("--adobe-start-date", type=click.DateTime())
@click.option("--adobe-end-date", default=None, type=click.DateTime())
@processor("adobe_password", "adobe_username")
def adobe_analytics_1_4(**kwargs):
    # Should handle valid combinations dimensions/metrics in the API
    return AdobeAnalytics14Reader(**extract_args("adobe_", kwargs))
