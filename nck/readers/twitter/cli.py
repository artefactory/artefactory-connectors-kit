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
from nck.readers.twitter.config import (
    ENTITY_ATTRIBUTES,
    GRANULARITIES,
    METRIC_GROUPS,
    PLACEMENTS,
    REPORT_TYPES,
    SEGMENTATION_TYPES,
)
from nck.readers.twitter.reader import TwitterReader
from nck.utils.args import extract_args
from nck.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS
from nck.utils.processor import processor


@click.command(name="read_twitter")
@click.option(
    "--twitter-consumer-key",
    required=True,
    help="API key, available in the 'Keys and tokens' section of your Twitter Developper App.",
)
@click.option(
    "--twitter-consumer-secret",
    required=True,
    help="API secret key, available in the 'Keys and tokens' section of your Twitter Developper App.",
)
@click.option(
    "--twitter-access-token",
    required=True,
    help="Access token, available in the 'Keys and tokens' section of your Twitter Developper App.",
)
@click.option(
    "--twitter-access-token-secret",
    required=True,
    help="Access token secret, available in the 'Keys and tokens' section of your Twitter Developper App.",
)
@click.option(
    "--twitter-account-id", required=True, help="Specifies the Twitter Account ID for which the data should be returned.",
)
@click.option(
    "--twitter-report-type",
    required=True,
    type=click.Choice(REPORT_TYPES),
    help="Specifies the type of report to collect: "
    "ANALYTICS (performance report, any kind of metrics), "
    "REACH (performance report, focus on reach and frequency metrics), "
    "ENTITY (entity configuration report)",
)
@click.option(
    "--twitter-entity",
    required=True,
    type=click.Choice(list(ENTITY_ATTRIBUTES.keys())),
    help="Specifies the entity type to retrieve data for.",
)
@click.option(
    "--twitter-entity-attribute",
    multiple=True,
    help="Specific to 'ENTITY' reports. " "Specifies the entity attribute (a.k.a. dimension) that should be returned.",
)
@click.option(
    "--twitter-granularity",
    type=click.Choice(GRANULARITIES),
    default="TOTAL",
    help="Specific to 'ANALYTICS' reports. Specifies how granular the retrieved data should be.",
)
@click.option(
    "--twitter-metric-group",
    multiple=True,
    type=click.Choice(METRIC_GROUPS),
    help="Specific to 'ANALYTICS' reports. Specifies the list of metrics (as a group) that should be returned: "
    "https://developer.twitter.com/en/docs/ads/analytics/overview/metrics-and-segmentation",
)
@click.option(
    "--twitter-placement",
    type=click.Choice(PLACEMENTS),
    default="ALL_ON_TWITTER",
    help="Specific to 'ANALYTICS' reports. Scopes the retrieved data to a particular placement.",
)
@click.option(
    "--twitter-segmentation-type",
    type=click.Choice(SEGMENTATION_TYPES),
    help="Specific to 'ANALYTICS' reports. Specifies how the retrieved data should be segmented: "
    "https://developer.twitter.com/en/docs/ads/analytics/overview/metrics-and-segmentation",
)
@click.option(
    "--twitter-platform",
    help="Specific to 'ANALYTICS' reports. Required if segmentation_type is set to 'DEVICES' or 'PLATFORM_VERSION'. "
    "To get possible values: GET targeting_criteria/locations",
)
@click.option(
    "--twitter-country",
    help="Specific to 'ANALYTICS' reports. Required if segmentation_type is set to 'CITIES', 'POSTAL_CODES', or 'REGION'. "
    "To get possible values: GET targeting_criteria/platforms",
)
@click.option("--twitter-start-date", type=click.DateTime(), help="Specifies report start date.")
@click.option(
    "--twitter-end-date", type=click.DateTime(), help="Specifies report end date (inclusive).",
)
@click.option(
    "--twitter-add-request-date-to-report",
    type=click.BOOL,
    default=False,
    help="If set to 'True', the date on which the request is made will appear on each report record.",
)
@click.option(
    "--twitter-date-range",
    type=click.Choice(DEFAULT_DATE_RANGE_FUNCTIONS.keys()),
    help=f"One of the available NCK default date ranges: {DEFAULT_DATE_RANGE_FUNCTIONS.keys()}",
)
@processor(
    "twitter_consumer_key", "twitter_consumer_secret", "twitter_access_token", "twitter_access_token_secret",
)
def twitter(**kwargs):
    return TwitterReader(**extract_args("twitter_", kwargs))
