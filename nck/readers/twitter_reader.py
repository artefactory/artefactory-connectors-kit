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

import logging
import click
from click import ClickException
import pandas as pd
from time import sleep
from itertools import chain
from datetime import datetime, timedelta

from nck.utils.args import extract_args
from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.streams.json_stream import JSONStream
from nck.helpers.twitter_helper import (
    REPORT_TYPES,
    ENTITY_OBJECTS,
    ENTITY_ATTRIBUTES,
    GRANULARITIES,
    METRIC_GROUPS,
    PLACEMENTS,
    SEGMENTATION_TYPES,
    JobTimeOutError,
)

from twitter_ads.client import Client
from twitter_ads.utils import split_list
from twitter_ads import API_VERSION
from twitter_ads.http import Request
from twitter_ads.cursor import Cursor

logging.basicConfig(level="INFO")
logger = logging.getLogger()

API_DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"
REP_DATEFORMAT = "%Y-%m-%d"
MAX_WAITING_SEC = 3600
MAX_ENTITY_IDS_PER_JOB = 20
MAX_CONCURRENT_JOBS = 100


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
    "--twitter-account-id",
    required=True,
    help="Specifies the Twitter Account ID for which the data should be returned.",
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
    type=click.Choice(list(ENTITY_OBJECTS.keys())),
    help="Specifies the entity type to retrieve data for.",
)
@click.option(
    "--twitter-entity-attribute",
    multiple=True,
    help="Specific to 'ENTITY' reports. Specifies the entity attribute (a.k.a. dimension) that should be returned.",
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
@click.option(
    "--twitter-start-date", type=click.DateTime(), help="Specifies report start date."
)
@click.option(
    "--twitter-end-date",
    type=click.DateTime(),
    help="Specifies report end date (inclusive).",
)
@click.option(
    "--twitter-add-request-date-to-report",
    type=click.BOOL,
    default=False,
    help="If set to 'True', the date on which the request is made will appear on each report record.",
)
@processor(
    "twitter_consumer_key",
    "twitter_consumer_secret",
    "twitter_access_token",
    "twitter_access_token_secret",
)
def twitter(**kwargs):
    return TwitterReader(**extract_args("twitter_", kwargs))


class TwitterReader(Reader):
    def __init__(
        self,
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret,
        account_id,
        report_type,
        entity,
        entity_attribute,
        granularity,
        metric_group,
        placement,
        segmentation_type,
        platform,
        country,
        start_date,
        end_date,
        add_request_date_to_report,
    ):
        # Authentification params
        self.client = Client(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        self.account = self.client.accounts(account_id)

        # General params
        self.report_type = report_type
        self.entity = entity
        self.start_date = start_date
        self.end_date = end_date + timedelta(days=1)
        self.add_request_date_to_report = add_request_date_to_report

        # Report params: ENTITY
        self.entity_attributes = list(entity_attribute)

        # Report params: ANALYTICS
        self.granularity = granularity
        self.metric_groups = list(metric_group)
        self.placement = placement
        self.segmentation_type = segmentation_type
        self.platform = platform
        self.country = country

        # Check input parameters

        if self.report_type == "ANALYTICS":

            if (
                self.segmentation_type in ["DEVICES", "PLATFORM VERSION"]
                and not self.platform
            ):
                raise ClickException("Please provide a value for 'platform'.")

            elif (
                self.segmentation_type in ["CITIES", "POSTAL_CODES", "REGION"]
                and not self.country
            ):
                raise ClickException("Please provide a value for 'country'.")

            if self.entity == "FUNDING_INSTRUMENT" and any(
                [
                    metric_group not in ["ENGAGEMENT", "BILLING"]
                    for metric_group in self.metric_groups
                ]
            ):
                raise ClickException(
                    "'FUNDING_INSTRUMENT' only accept the 'ENGAGEMENT' and 'BILLING' metric groups."
                )

            if "MOBILE_CONVERSION" in self.metric_groups and len(
                self.metric_groups > 1
            ):
                raise ClickException(
                    "'MOBILE_CONVERSION' data should be requested separately."
                )

        elif self.report_type == "REACH":

            if self.entity not in ["CAMPAIGN", "FUNDING_INSTRUMENT"]:
                raise ClickException(
                    "'REACH' reports only accept the 'CAMPAIGN' and 'FUNDING_INSTRUMENT' entities."
                )

        elif self.report_type == "ENTITY":

            if not all(
                [
                    attr in ENTITY_ATTRIBUTES[self.entity]
                    for attr in self.entity_attributes
                ]
            ):
                raise ClickException(
                    f"Available attributes for '{self.entity}' are: {ENTITY_ATTRIBUTES[self.entity]}"
                )

    def get_daily_period_items(self):
        """
        Returns a list of datetime instances representing each date contained
        in the requested period. Useful when granularity is set to 'DAY'.
        """

        period_items = []
        current_date = self.start_date

        while current_date < self.end_date:
            period_items.append(current_date)
            current_date += timedelta(days=1)

        return period_items

    def get_active_entity_ids(self):
        """
        Step 1 of 'ANALYTICS' report generation process:
        Returns a list containing the ids of active entities over the requested time period
        Documentation: https://developer.twitter.com/en/docs/ads/analytics/api-reference/active-entities
        """

        active_entities = ENTITY_OBJECTS[self.entity].active_entities(
            self.account, self.start_date, self.end_date
        )
        return [obj["entity_id"] for obj in active_entities]

    def get_job_ids(self, entity_ids):
        """
        Step 2 of 'ANALYTICS' report generation process:
        Create asynchronous analytics jobs and return their ids for progress tracking
        Documentation: https://developer.twitter.com/en/docs/ads/analytics/api-reference/asynchronous
        """

        return [
            ENTITY_OBJECTS[self.entity]
            .queue_async_stats_job(
                self.account,
                chunk_entity_ids,
                self.metric_groups,
                granularity=self.granularity,
                placement=self.placement,
                start_time=self.start_date,
                end_time=self.end_date,
                segmentation_type=self.segmentation_type,
                platform=self.platform,
                country=self.country,
            )
            .id
            for chunk_entity_ids in split_list(entity_ids, MAX_ENTITY_IDS_PER_JOB)
        ]

    def get_job_result(self, job_id):
        """
        Step 3 of 'ANALYTICS' report generation process:
        Get job info to track its progress (job_result.status) and download report once completed (job_result.url)
        Documentation: https://developer.twitter.com/en/docs/ads/analytics/api-reference/asynchronous
        """

        return (
            ENTITY_OBJECTS[self.entity]
            .async_stats_job_result(self.account, job_ids=[job_id])
            .first
        )

    def get_raw_analytics_response(self, job_result):
        """
        Step 4 of 'ANALYTICS' report generation process:
        Download raw response from job once completed
        Documentation: https://developer.twitter.com/en/docs/ads/analytics/api-reference/asynchronous
        """

        return ENTITY_OBJECTS[self.entity].async_stats_job_data(
            self.account, url=job_result.url
        )

    def parse(self, raw_analytics_response):
        """
        Parse a single raw response into a generator of JSON-like records.
        """

        for entity_resp in raw_analytics_response["data"]:

            for entity_data in entity_resp["id_data"]:

                entity_df = pd.DataFrame(entity_data["metrics"]).fillna(0)
                entity_df["id"] = entity_resp["id"]
                if self.granularity == "DAY":
                    entity_df["date"] = [
                        item.strftime(REP_DATEFORMAT)
                        for item in self.get_daily_period_items()
                    ]
                if self.segmentation_type:
                    entity_df[self.segmentation_type.lower()] = entity_data["segment"][
                        "segment_name"
                    ]

                yield from entity_df.to_dict("records")

    def get_analytics_report(self, job_ids):
        """
        Get 'ANALYTICS' report through the 'Asynchronous Analytics' endpoint of Twitter Ads API.
        Documentation: https://developer.twitter.com/en/docs/ads/analytics/api-reference/asynchronous
        """

        all_responses = []

        for job_id in job_ids:

            logging.info(f"Processing job_id: {job_id}")

            job_result = self.get_job_result(job_id)
            waiting_sec = 2

            while job_result.status == "PROCESSING":
                logging.info(f"Waiting {waiting_sec} seconds for job to be completed")
                sleep(waiting_sec)
                if waiting_sec > MAX_WAITING_SEC:
                    raise JobTimeOutError("Waited too long for job to be completed")
                waiting_sec *= 2
                job_result = self.get_job_result(job_id)

            raw_analytics_response = self.get_raw_analytics_response(job_result)
            all_responses.append(self.parse(raw_analytics_response))

        return chain(*all_responses)

    def get_entity_report(self):
        """
        Get 'ENTITY' report through 'Core Entity' endpoints of Twitter Ads API.
        Documentation: https://developer.twitter.com/en/docs/ads/campaign-management/api-reference
        """

        ACCOUNT_CHILD_OBJECTS = {
            "FUNDING_INSTRUMENT": self.account.funding_instruments(),
            "CAMPAIGN": self.account.campaigns(),
            "LINE_ITEM": self.account.line_items(),
            "MEDIA_CREATIVE": self.account.media_creatives(),
            "PROMOTED_TWEET": self.account.promoted_tweets(),
        }

        yield from [
            {attr: getattr(entity_obj, attr, None) for attr in self.entity_attributes}
            for entity_obj in ACCOUNT_CHILD_OBJECTS[self.entity]
        ]

    def get_reach_report(self):
        """
        Get 'REACH' report through the 'Reach and Average Frequency' endpoint of Twitter Ads API.
        Documentation: https://developer.twitter.com/en/docs/ads/analytics/api-reference/reach
        """

        resource = (
            "/"
            + API_VERSION
            + f"/stats/accounts/{self.account.id}/reach/{self.entity.lower()}s"
        )
        entity_ids = self.get_active_entity_ids()

        for chunk_entity_ids in split_list(entity_ids, MAX_ENTITY_IDS_PER_JOB):
            params = {
                "account_id": self.account.id,
                f"{self.entity.lower()}_ids": ",".join(entity_ids),
                "start_time": self.start_date.strftime(API_DATEFORMAT),
                "end_time": self.end_date.strftime(API_DATEFORMAT),
            }
            request = Request(self.client, "get", resource, params=params)
            yield from Cursor(None, request)

    def add_date_if_necessary(self, record):
        """
        Add request_date, period_start_date and/or period_end_date to a JSON-like record.
        """

        if self.add_request_date_to_report:
            record["request_date"] = datetime.today().strftime(REP_DATEFORMAT)

        if (
            self.report_type == "ANALYTICS" and self.granularity == "TOTAL"
        ) or self.report_type == "REACH":
            record["period_start_date"] = self.start_date.strftime(REP_DATEFORMAT)
            record["period_end_date"] = (self.end_date - timedelta(days=1)).strftime(
                REP_DATEFORMAT
            )

        return record

    def read(self):

        if self.report_type == "ANALYTICS":
            entity_ids = self.get_active_entity_ids()

            total_jobs = (len(entity_ids) // MAX_ENTITY_IDS_PER_JOB) + 1
            logging.info(f"Processing a total of {total_jobs} jobs")

            data = []
            for chunk_entity_ids in split_list(
                entity_ids, MAX_ENTITY_IDS_PER_JOB * MAX_CONCURRENT_JOBS
            ):
                job_ids = self.get_job_ids(chunk_entity_ids)
                data += self.get_analytics_report(job_ids)

        elif self.report_type == "REACH":
            data = self.get_reach_report()

        elif self.report_type == "ENTITY":
            data = self.get_entity_report()

        def result_generator():
            for record in data:
                yield self.add_date_if_necessary(record)

        yield JSONStream("results_" + self.account.id, result_generator())
