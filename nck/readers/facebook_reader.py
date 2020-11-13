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

import logging
import click
import re
from math import ceil
from click import ClickException
from datetime import datetime
from tenacity import retry, wait_none, wait_exponential, stop_after_delay, stop_after_attempt

from nck.readers.reader import Reader
from nck.utils.args import extract_args
from nck.commands.command import processor
from nck.streams.normalized_json_stream import NormalizedJSONStream
from nck.helpers.facebook_helper import (
    FACEBOOK_OBJECTS,
    DATE_PRESETS,
    BREAKDOWNS,
    ACTION_BREAKDOWNS,
    get_action_breakdown_filters,
    get_field_values,
    generate_batches,
    monitor_usage,
)

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adspixel import AdsPixel
from facebook_business.adobjects.adreportrun import AdReportRun

DATEFORMAT = "%Y-%m-%d"

OBJECT_CREATION_MAPPING = {
    "account": AdAccount,
    "campaign": Campaign,
    "adset": AdSet,
    "ad": Ad,
    "creative": AdCreative,
    "pixel": AdsPixel,
}

EDGE_MAPPING = {
    "account": ["campaign", "adset", "ad", "creative", "pixel"],
    "campaign": ["adset", "ad"],
    "adset": ["ad", "creative"],
    "ad": ["creative"],
}

EDGE_QUERY_MAPPING = {
    "campaign": lambda obj: obj.get_campaigns(),
    "adset": lambda obj: obj.get_ad_sets(),
    "ad": lambda obj: obj.get_ads(),
    "creative": lambda obj: obj.get_ad_creatives(),
    "pixel": lambda obj: obj.get_ads_pixels(),
}

BATCH_SIZE_LIMIT = 50


def check_object_id(ctx, param, values):
    try:
        [int(value) for value in values]
        return values
    except ValueError:
        raise ClickException("Wrong format. Ad object IDs should only contains digits.")


@click.command(name="read_facebook")
@click.option("--facebook-app-id", default="", help="Not mandatory for AdsInsights reporting if access-token provided")
@click.option(
    "--facebook-app-secret", default="", help="Not mandatory for AdsInsights reporting if access-token provided"
)
@click.option("--facebook-access-token", required=True)
@click.option("--facebook-object-id", required=True, multiple=True, callback=check_object_id)
@click.option("--facebook-object-type", type=click.Choice(FACEBOOK_OBJECTS), default="account")
@click.option("--facebook-level", type=click.Choice(FACEBOOK_OBJECTS), default="ad", help="Granularity of result")
@click.option(
    "--facebook-ad-insights",
    type=click.BOOL,
    default=True,
    help="https://developers.facebook.com/docs/marketing-api/insights",
)
@click.option(
    "--facebook-breakdown",
    multiple=True,
    type=click.Choice(BREAKDOWNS),
    help="https://developers.facebook.com/docs/marketing-api/insights/breakdowns/",
)
@click.option(
    "--facebook-action-breakdown",
    multiple=True,
    type=click.Choice(ACTION_BREAKDOWNS),
    help="https://developers.facebook.com/docs/marketing-api/insights/breakdowns#actionsbreakdown",
)
@click.option("--facebook-field", multiple=True, help="API fields, following Artefact format")
@click.option("--facebook-time-increment")
@click.option("--facebook-start-date", type=click.DateTime())
@click.option("--facebook-end-date", type=click.DateTime())
@click.option("--facebook-date-preset", type=click.Choice(DATE_PRESETS))
@click.option(
    "--facebook-add-date-to-report",
    type=click.BOOL,
    default=False,
    help="If set to true, the date of the request will appear in the report",
)
@processor("facebook_app_secret", "facebook_access_token")
def facebook(**kwargs):
    return FacebookReader(**extract_args("facebook_", kwargs))


class FacebookReader(Reader):
    def __init__(
        self,
        app_id,
        app_secret,
        access_token,
        object_id,
        object_type,
        level,
        ad_insights,
        breakdown,
        action_breakdown,
        field,
        time_increment,
        start_date,
        end_date,
        date_preset,
        add_date_to_report,
    ):
        # Authentication inputs
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.api = FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)

        # Level inputs
        self.object_ids = object_id
        self.object_type = object_type
        self.level = level

        # Report inputs
        self.ad_insights = ad_insights
        self.breakdowns = list(breakdown)
        self.action_breakdowns = list(action_breakdown)
        self.fields = list(field)
        self._field_paths = [re.split(r"[\]\[]+", f.strip("]")) for f in self.fields]
        self._api_fields = list({f[0] for f in self._field_paths if f[0] not in self.breakdowns})

        # Date inputs
        self.time_increment = time_increment or False
        self.start_date = start_date
        self.end_date = end_date
        self.date_preset = date_preset
        self.add_date_to_report = add_date_to_report

        # Validate inputs
        self.validate_inputs()

    def validate_inputs(self):
        """
        Validate combination of input parameters (triggered in FacebookReader constructor).
        """
        self.validate_object_type_and_level_combination()
        self.validate_ad_insights_level()
        self.validate_ad_insights_breakdowns()
        self.validate_ad_insights_action_breakdowns()
        self.validate_ad_management_inputs()

    def validate_object_type_and_level_combination(self):

        if (self.level != self.object_type) and (self.level not in EDGE_MAPPING[self.object_type]):
            raise ClickException(
                f"Wrong query. Asked level ({self.level}) is not compatible with object type ({self.object_type}).\
                Please choose level from: {[self.object_type] + EDGE_MAPPING[self.object_type]}"
            )

    def validate_ad_insights_level(self):

        if self.ad_insights:
            if self.level == "creative" or self.object_type == "creative":
                raise ClickException(
                    f"Wrong query. The 'creative' level is not available in Ad Insights queries.\
                    Accepted levels: {FACEBOOK_OBJECTS[1:]}"
                )

    def validate_ad_insights_breakdowns(self):

        if self.ad_insights:
            missing_breakdowns = {
                f[0] for f in self._field_paths if (f[0] in BREAKDOWNS) and (f[0] not in self.breakdowns)
            }
            if missing_breakdowns != set():
                raise ClickException(f"Wrong query. Please add to Breakdowns: {missing_breakdowns}")

    def validate_ad_insights_action_breakdowns(self):

        if self.ad_insights:
            missing_action_breakdowns = {
                flt
                for f in self._field_paths
                for flt in get_action_breakdown_filters(f)
                if flt not in self.action_breakdowns
            }
            if missing_action_breakdowns != set():
                raise ClickException(f"Wrong query. Please add to Action Breakdowns: {missing_action_breakdowns}")

    def validate_ad_management_inputs(self):

        if not self.ad_insights:
            if self.breakdowns != [] or self.action_breakdowns != []:
                raise ClickException(
                    "Wrong query. Ad Management queries do not accept Breakdowns nor Action Breakdowns."
                )

            if self.time_increment:
                raise ClickException("Wrong query. Ad Management queries do not accept the time_increment parameter.")

    def get_params(self):
        """
        Build the request parameters that will be sent to the API:
        - If Ad Insights query: breakdown, action_breakdowns, level, time_range and date_preset
        - If Ad Management query at the campaign, adset or ad level: time_range and date_preset
        """
        params = {}

        if self.ad_insights:

            params["breakdowns"] = self.breakdowns
            params["action_breakdowns"] = self.action_breakdowns
            params["level"] = self.level
            self.add_period_to_params(params)

        else:
            if self.level in ["campaign", "adset", "ad"]:
                self.add_period_to_params(params)

        return params

    def add_period_to_params(self, params):
        """
        Add the time_increment, time_range and/or date_preset keys to parameters.
        - time_increment: available in Ad Insights queries
        - time_range and date_preset: available in Ad Insights queries,
        and in Ad Management queries at the campaign, adset or ad levels only
        """
        if self.ad_insights and self.time_increment:
            params["time_increment"] = self.time_increment

        if self.ad_insights or self.level in ["campaign", "adset", "ad"]:
            if self.start_date and self.end_date:
                logging.info("Date format used for request: start_date and end_date")
                params["time_range"] = self.create_time_range()
            elif self.date_preset:
                logging.info("Date format used for request: date_preset")
                params["date_preset"] = self.date_preset
            else:
                logging.warning("No date range provided - Last 30 days by default")
                logging.warning(
                    "https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights#parameters"
                )

    def create_time_range(self):
        return {"since": self.start_date.strftime(DATEFORMAT), "until": self.end_date.strftime(DATEFORMAT)}

    def create_object(self, object_id):
        """
        Create a Facebook object based on the provided object_type and object_id.
        """
        if self.object_type == "account":
            object_id = "act_" + object_id
        obj = OBJECT_CREATION_MAPPING[self.object_type](object_id)

        return obj

    def query_ad_insights(self, fields, params, object_id):
        """
        Ad Insights documentation:
        https://developers.facebook.com/docs/marketing-api/insights
        """

        logging.info(f"Running Facebook Ad Insights query on {self.object_type}_id: {object_id}")

        # Step 1 - Create Facebook object
        obj = self.create_object(object_id)
        # Step 2 - Run Ad Insights query on Facebook object
        report_job = self._get_report(obj, fields, params)

        yield from report_job.get_result()

    @retry(wait=wait_none(), stop=stop_after_attempt(3))
    def _get_report(self, obj, fields, params):
        async_job = obj.get_insights(fields=fields, params=params, is_async=True)
        self._wait_for_100_percent_completion(async_job)
        self._wait_for_complete_report(async_job)
        return async_job

    @retry(wait=wait_exponential(multiplier=60, max=300), stop=stop_after_delay(2400))
    def _wait_for_100_percent_completion(self, async_job):
        async_job.api_get()
        percent_completion = async_job[AdReportRun.Field.async_percent_completion]
        status = async_job[AdReportRun.Field.async_status]
        logging.info(f"{status}: {percent_completion}%")
        if status == "Job Failed":
            logging.info(status)
        elif percent_completion < 100:
            raise Exception(f"{status}: {percent_completion}")

    @retry(wait=wait_exponential(multiplier=10, max=60), stop=stop_after_delay(300))
    def _wait_for_complete_report(self, async_job):
        async_job.api_get()
        status = async_job[AdReportRun.Field.async_status]
        if status == "Job Running":
            raise Exception(status)
        logging.info(status)

    def query_ad_management(self, fields, params, object_id):
        """
        Ad Management documentation:
        https://developers.facebook.com/docs/marketing-api/reference/
        Supported object nodes: AdAccount, Campaign, AdSet, Ad and AdCreative
        """

        logging.info(f"Running Ad Management query on {self.object_type}_id: {object_id}")

        # Step 1 - Create Facebook object
        obj = self.create_object(object_id)

        # Step 2 - Run Ad Management query on the Facebook object itself,
        # or on one of its edges (depending on the specified level)
        if self.level == self.object_type:
            yield obj.api_get(fields=fields, params=params)
        else:
            edge_objs = EDGE_QUERY_MAPPING[self.level](obj)
            yield from self.get_edge_objs_records(edge_objs, fields, params)

    def get_edge_objs_records(self, edge_objs, fields, params):
        """
        Make batch Ad Management requests on a set of edge objects
        (edge_objs being a facebook_business.api.Cursor object).
        """

        total_edge_objs = edge_objs._total_count
        total_batches = ceil(total_edge_objs / BATCH_SIZE_LIMIT)
        logging.info(f"Making {total_batches} batch requests on a total of {total_edge_objs} {self.level}s")

        for batch in generate_batches(edge_objs, BATCH_SIZE_LIMIT):

            # Create batch
            api_batch = self.api.new_batch()
            batch_responses = []

            # Add each campaign request to batch
            for obj in batch:

                def callback_success(response):
                    batch_responses.append(response.json())
                    monitor_usage(response)

                def callback_failure(response):
                    raise response.error()

                obj.api_get(
                    fields=fields, params=params, batch=api_batch, success=callback_success, failure=callback_failure
                )

            # Execute batch
            api_batch.execute()

            yield from batch_responses

    def format_and_yield(self, record):
        """
        Parse a single record into an {item: value} dictionary.
        """
        report = {}

        for field_path in self._field_paths:
            field_values = get_field_values(record, field_path, self.action_breakdowns, visited=[])
            if field_values:
                report.update(field_values)

        if self.add_date_to_report:
            report["date"] = datetime.today().strftime(DATEFORMAT)

        yield report

    def result_generator(self, data):
        """
        Parse all records into an {item: value} dictionary.
        """
        for record in data:
            yield from self.format_and_yield(record)

    def get_data_for_object(self, object_id):
        """
        Run an API query (Ad Insights or Ad Management) on a single object_id.
        """
        params = self.get_params()

        if self.ad_insights:
            data = self.query_ad_insights(self._api_fields, params, object_id)
        else:
            data = self.query_ad_management(self._api_fields, params, object_id)

        yield from self.result_generator(data)

    def get_data(self):
        """
        Run API queries on all object_ids.
        """
        for object_id in self.object_ids:
            yield from self.get_data_for_object(object_id)

    def read(self):

        yield NormalizedJSONStream("results_" + self.object_type + "_" + "_".join(self.object_ids), self.get_data())
