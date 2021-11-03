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
from ack.readers.google_analytics.reader import GoogleAnalyticsReader
from ack.utils.args import extract_args
from ack.utils.processor import processor


@click.command(name="read_ga")
@click.option("--ga-access-token", default=None)
@click.option("--ga-refresh-token", required=True)
@click.option("--ga-client-id", required=True)
@click.option("--ga-client-secret", required=True)
@click.option("--ga-view-id", default=[], multiple=True)
@click.option("--ga-account-id", default=[], multiple=True)
@click.option("--ga-dimension", multiple=True)
@click.option("--ga-metric", multiple=True)
@click.option("--ga-segment-id", multiple=True)
@click.option("--ga-start-date", type=click.DateTime(), default=None)
@click.option("--ga-end-date", type=click.DateTime(), default=None)
@click.option("--ga-date-range", nargs=2, type=click.DateTime(), default=None)
@click.option(
    "--ga-day-range", type=click.Choice(["PREVIOUS_DAY", "LAST_30_DAYS", "LAST_7_DAYS", "LAST_90_DAYS"]), default=None
)
@click.option("--ga-sampling-level", type=click.Choice(["SMALL", "DEFAULT", "LARGE"]), default="LARGE")
@click.option("--ga-add-view", is_flag=True)
@processor("ga_access_token", "ga_refresh_token", "ga_client_secret")
def google_analytics(**kwargs):
    # Should handle valid combinations dimensions/metrics in the API
    return GoogleAnalyticsReader(**extract_args("ga_", kwargs))
