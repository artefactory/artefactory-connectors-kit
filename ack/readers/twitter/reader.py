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

from datetime import datetime, timedelta
from itertools import chain

from click import ClickException
from ack.config import logger
from ack.readers.reader import Reader
from ack.readers.twitter.config import (
    API_DATEFORMAT,
    # MAX_WAITING_SEC,
    ENTITY_ATTRIBUTES,
    ENTITY_OBJECTS,
    MAX_CONCURRENT_JOBS,
    MAX_ENTITY_IDS_PER_JOB,
    REP_DATEFORMAT,
)
from ack.streams.json_stream import JSONStream
from ack.utils.date_handler import build_date_range
from tenacity import retry, stop_after_delay, wait_exponential
from twitter_ads import API_VERSION
from twitter_ads.client import Client

# from twitter_ads.creative import TweetPreview
from twitter_ads.creative import CardsFetch
from twitter_ads.cursor import Cursor
from twitter_ads.http import Request
from twitter_ads.utils import split_list


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
        date_range,
    ):
        # Authentication inputs
        self.client = Client(consumer_key, consumer_secret, access_token, access_token_secret)
        self.account = self.client.accounts(account_id)

        # General inputs
        self.report_type = report_type
        self.entity = entity
        self.start_date, self.end_date = build_date_range(start_date, end_date, date_range)
        self.end_date = self.end_date + timedelta(days=1)
        self.add_request_date_to_report = add_request_date_to_report

        # Report inputs: ENTITY
        self.entity_attributes = list(entity_attribute)

        # Report inputs: ANALYTICS
        self.granularity = granularity
        self.metric_groups = list(metric_group)
        self.placement = placement
        self.segmentation_type = segmentation_type
        self.platform = platform
        self.country = country

        # Validate inputs
        self.validate_inputs()

    def validate_inputs(self):
        """
        Validate combination of input parameters (triggered in TwitterReader constructor).
        """

        self.validate_analytics_segmentation()
        self.validate_analytics_metric_groups()
        self.validate_analytics_entity()
        self.validate_reach_entity()
        self.validate_entity_attributes()

    def validate_analytics_segmentation(self):

        if self.report_type == "ANALYTICS":
            if self.segmentation_type in ["DEVICES", "PLATFORM VERSION"] and not self.platform:
                raise ClickException("Please provide a value for 'platform'.")

            elif self.segmentation_type in ["CITIES", "POSTAL_CODES", "REGION"] and not self.country:
                raise ClickException("Please provide a value for 'country'.")

    def validate_analytics_metric_groups(self):

        if self.report_type == "ANALYTICS":

            if self.entity == "FUNDING_INSTRUMENT" and any(
                [metric_group not in ["ENGAGEMENT", "BILLING"] for metric_group in self.metric_groups]
            ):
                raise ClickException("'FUNDING_INSTRUMENT' only accept the 'ENGAGEMENT' and 'BILLING' metric groups.")

            if "MOBILE_CONVERSION" in self.metric_groups and len(self.metric_groups) > 1:
                raise ClickException("'MOBILE_CONVERSION' data should be requested separately.")

    def validate_analytics_entity(self):

        if self.report_type == "ANALYTICS":

            if self.entity == "CARD":
                raise ClickException(f"'ANALYTICS' reports only accept following entities: {list(ENTITY_OBJECTS.keys())}.")

    def validate_reach_entity(self):

        if self.report_type == "REACH":

            if self.entity not in ["CAMPAIGN", "FUNDING_INSTRUMENT"]:
                raise ClickException("'REACH' reports only accept the following entities: CAMPAIGN, FUNDING_INSTRUMENT.")

    def validate_entity_attributes(self):

        if self.report_type == "ENTITY":

            if not all([attr in ENTITY_ATTRIBUTES[self.entity] for attr in self.entity_attributes]):
                raise ClickException(f"Available attributes for '{self.entity}' are: {ENTITY_ATTRIBUTES[self.entity]}")

    def get_analytics_report(self, job_ids):
        """
        Get 'ANALYTICS' report through the 'Asynchronous Analytics' endpoint of Twitter Ads API.
        Documentation: https://developer.twitter.com/en/docs/ads/analytics/api-reference/asynchronous
        """

        all_responses = []

        for job_id in job_ids:

            logger.info(f"Processing job_id: {job_id}")

            # job_result = self.get_job_result(job_id)
            # waiting_sec = 2

            # while job_result.status == "PROCESSING":
            #     logger.info(f"Waiting {waiting_sec} seconds for job to be completed")
            #     sleep(waiting_sec)
            #     if waiting_sec > MAX_WAITING_SEC:
            #         raise JobTimeOutError("Waited too long for job to be completed")
            #     waiting_sec *= 2
            #     job_result = self.get_job_result(job_id)

            job_result = self._waiting_for_job_to_complete(job_id)
            raw_analytics_response = self.get_raw_analytics_response(job_result)
            all_responses.append(self.parse(raw_analytics_response))

        return chain(*all_responses)

    def get_active_entity_ids(self):
        """
        Step 1 of 'ANALYTICS' report generation process:
        Returns a list containing the ids of active entities over the requested time period
        Documentation: https://developer.twitter.com/en/docs/ads/analytics/api-reference/active-entities
        """

        active_entities = ENTITY_OBJECTS[self.entity].active_entities(self.account, self.start_date, self.end_date)
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

    @retry(
        wait=wait_exponential(multiplier=1, min=60, max=3600), stop=stop_after_delay(36000),
    )
    def _waiting_for_job_to_complete(self, job_id):
        """
        Retrying to get job_result until job status is 'COMPLETED'.
        """
        job_result = self.get_job_result(job_id)
        if job_result.status == "PROCESSING":
            raise Exception(f"Job {job_id} is still running.")
        else:
            return job_result

    def get_job_result(self, job_id):
        """
        Step 3 of 'ANALYTICS' report generation process:
        Get job info to track its progress (job_result.status) and download report once completed (job_result.url)
        Documentation: https://developer.twitter.com/en/docs/ads/analytics/api-reference/asynchronous
        """

        return ENTITY_OBJECTS[self.entity].async_stats_job_result(self.account, job_ids=[job_id]).first

    def get_raw_analytics_response(self, job_result):
        """
        Step 4 of 'ANALYTICS' report generation process:
        Download raw response from job once completed
        Documentation: https://developer.twitter.com/en/docs/ads/analytics/api-reference/asynchronous
        """

        return ENTITY_OBJECTS[self.entity].async_stats_job_data(self.account, url=job_result.url)

    def parse(self, raw_analytics_response):
        """
        Parse a single raw response into a generator of JSON-like records.
        """

        for entity_resp in raw_analytics_response["data"]:
            for entity_data in entity_resp["id_data"]:
                entity_records = [
                    {
                        "id": entity_resp["id"],
                        **{
                            mt: 0 if entity_data["metrics"][mt] is None else entity_data["metrics"][mt][i]
                            for mt in entity_data["metrics"]
                        },
                    }
                    for i in range(raw_analytics_response["time_series_length"])
                ]
                entity_records = self.add_daily_timestamps(entity_records)
                entity_records = self.add_segment(entity_records, entity_data)
                yield from entity_records

    def add_daily_timestamps(self, entity_records):
        """
        Add daily timestamps to a list of records, if granularity is 'DAY'.
        """

        if self.granularity == "DAY":
            period_items = self.get_daily_period_items()
            return [
                {**entity_records[i], "date": period_items[i].strftime(REP_DATEFORMAT)} for i in range(len(entity_records))
            ]
        return entity_records

    def get_daily_period_items(self):
        """
        Returns a list of datetime instances representing each date contained
        in the requested period. Useful when granularity is set to 'DAY'.
        """

        delta = self.end_date - self.start_date
        return [self.start_date + timedelta(days=i) for i in range(delta.days)]

    def add_segment(self, entity_records, entity_data):
        """
        Add segment to a list of records, if a segmentation_type is requested.
        """

        if self.segmentation_type:
            entity_segment = entity_data["segment"]["segment_name"]
            return [{**rec, self.segmentation_type.lower(): entity_segment} for rec in entity_records]
        return entity_records

    def get_campaign_management_report(self):
        """
        Get 'ENTITY' report through 'Campaign Management' endpoints of Twitter Ads API.
        Supported entities: FUNDING_INSTRUMENT, CAMPAIGN, LINE_ITEM, MEDIA_CREATIVE, PROMOTED_TWEET
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

    def get_cards_report(self):
        """
        Get 'ENTITY' report through the 'Creatives' endpoint of Twitter Ads API.
        Supported entities: CARD
        Documentation: https://developer.twitter.com/en/docs/ads/creatives/api-reference/
        """

        for tweet in self.get_published_tweets():
            if "card_uri" in tweet:
                card_fetch = self.get_card_fetch(card_uri=tweet["card_uri"])
                card_attributes = {attr: getattr(card_fetch, attr, None) for attr in self.entity_attributes}
                record = {
                    "tweet_id": tweet["tweet_id"],
                    "card_uri": tweet["card_uri"],
                    **card_attributes,
                }
                yield record

    def get_published_tweets(self):
        """
        Step 1 of 'ENTITY - CARD' report generation process:
        Returns details on 'PUBLISHED' tweets, as a generator of dictionnaries
        Documentation: https://developer.twitter.com/en/docs/ads/creatives/api-reference/tweets
        """

        resource = f"/{API_VERSION}/accounts/{self.account.id}/tweets"
        params = {"tweet_type": "PUBLISHED"}
        request = Request(self.client, "get", resource, params=params)

        yield from Cursor(None, request)

    def get_card_fetch(self, card_uri):
        """
        Step 2 of 'ENTITY - CARD' report generation process:
        Returns the CartFetch object associated with a specific card_uri
        Documentation: https://developer.twitter.com/en/docs/ads/creatives/api-reference/cards-fetch
        """

        return CardsFetch.load(self.account, card_uris=[card_uri]).first

    def get_reach_report(self):
        """
        Get 'REACH' report through the 'Reach and Average Frequency' endpoint of Twitter Ads API.
        Documentation: https://developer.twitter.com/en/docs/ads/analytics/api-reference/reach
        """

        resource = f"/{API_VERSION}/stats/accounts/{self.account.id}/reach/{self.entity.lower()}s"
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

    def add_request_or_period_dates(self, record):
        """
        Add request_date, period_start_date and/or period_end_date to a JSON-like record.
        """

        def check_add_period_date_to_report():
            return (self.report_type == "ANALYTICS" and self.granularity == "TOTAL") or self.report_type == "REACH"

        if self.add_request_date_to_report:
            record["request_date"] = datetime.today().strftime(REP_DATEFORMAT)

        if check_add_period_date_to_report():
            record["period_start_date"] = self.start_date.strftime(REP_DATEFORMAT)
            record["period_end_date"] = (self.end_date - timedelta(days=1)).strftime(REP_DATEFORMAT)

        return record

    def read(self):

        if self.report_type == "ANALYTICS":
            entity_ids = self.get_active_entity_ids()

            total_jobs = (len(entity_ids) // MAX_ENTITY_IDS_PER_JOB) + 1
            logger.info(f"Processing a total of {total_jobs} jobs")

            data = []
            for chunk_entity_ids in split_list(entity_ids, MAX_ENTITY_IDS_PER_JOB * MAX_CONCURRENT_JOBS):
                job_ids = self.get_job_ids(chunk_entity_ids)
                data += self.get_analytics_report(job_ids)

        elif self.report_type == "REACH":
            data = self.get_reach_report()

        elif self.report_type == "ENTITY":
            if self.entity == "CARD":
                data = self.get_cards_report()
            else:
                data = self.get_campaign_management_report()

        def result_generator():
            for record in data:
                yield self.add_request_or_period_dates(record)

        yield JSONStream("results_" + self.account.id, result_generator())
