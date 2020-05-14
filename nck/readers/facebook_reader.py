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
from click import ClickException
from datetime import datetime

from nck.readers.reader import Reader
from nck.utils.args import extract_args
from nck.commands.command import processor
from nck.utils.retry import retry
from nck.streams.normalized_json_stream import NormalizedJSONStream
from nck.helpers.facebook_helper import (
    FACEBOOK_OBJECTS,
    DATE_PRESETS,
    BREAKDOWNS,
    ACTION_BREAKDOWNS,
    get_action_breakdown_filters,
    get_field_values,
)

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative

DATEFORMAT = "%Y-%m-%d"

OBJECT_CREATION_MAPPING = {
    "account": AdAccount,
    "campaign": Campaign,
    "adset": AdSet,
    "ad": Ad,
    "creative": AdCreative,
}

EDGE_MAPPING = {
    "account": ["campaign", "adset", "ad", "creative"],
    "campaign": ["adset", "ad"],
    "adset": ["ad", "creative"],
    "ad": ["creative"],
}


def check_object_id(ctx, param, values):
    try:
        [int(value) for value in values]
        return values
    except ValueError:
        raise ClickException("Wrong format. Ad object IDs should only contains digits.")


@click.command(name="read_facebook")
@click.option(
    "--facebook-app-id",
    default="",
    help="Not mandatory for AdsInsights reporting if access-token provided",
)
@click.option(
    "--facebook-app-secret",
    default="",
    help="Not mandatory for AdsInsights reporting if access-token provided",
)
@click.option("--facebook-access-token", required=True)
@click.option(
    "--facebook-object-id", required=True, multiple=True, callback=check_object_id
)
@click.option(
    "--facebook-object-type", type=click.Choice(FACEBOOK_OBJECTS), default="account"
)
@click.option(
    "--facebook-level",
    type=click.Choice(FACEBOOK_OBJECTS),
    default="ad",
    help="Granularity of result",
)
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
@click.option(
    "--facebook-field", multiple=True, help="API fields, following Artefact format"
)
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
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token

        self.object_ids = object_id
        self.object_type = object_type
        self.level = level

        self.ad_insights = ad_insights
        self.breakdowns = list(breakdown)
        self.action_breakdowns = list(action_breakdown)
        self.fields = list(field)
        self._field_paths = [re.split(r"[\]\[]+", f.strip("]")) for f in self.fields]
        self._api_fields = list(
            {f[0] for f in self._field_paths if f[0] not in self.breakdowns}
        )

        self.time_increment = time_increment or False
        self.start_date = start_date
        self.end_date = end_date
        self.date_preset = date_preset
        self.add_date_to_report = add_date_to_report

        # Check input parameters

        if (self.level != self.object_type) and (
            self.level not in EDGE_MAPPING[self.object_type]
        ):
            raise ClickException(
                f"Wrong query. Asked level ({self.level}) is not compatible with object type ({self.object_type}).\
                Please choose level from: {[self.object_type] + EDGE_MAPPING[self.object_type]}"
            )

        if self.ad_insights:

            if self.level == "creative" or self.object_type == "creative":
                raise ClickException(
                    f"Wrong query. The 'creative' level is not available in AdInsights queries.\
                    Accepted levels: {FACEBOOK_OBJECTS[1:]}"
                )

            missing_breakdowns = {
                f[0]
                for f in self._field_paths
                if (f[0] in BREAKDOWNS) and (f[0] not in self.breakdowns)
            }
            if missing_breakdowns != set():
                raise ClickException(
                    f"Wrong query. Please add to Breakdowns: {missing_breakdowns}"
                )

            missing_action_breakdowns = {
                flt
                for f in self._field_paths
                for flt in get_action_breakdown_filters(f)
                if flt not in self.action_breakdowns
            }
            if missing_action_breakdowns != set():
                raise ClickException(
                    f"Wrong query. Please add to Action Breakdowns: {missing_action_breakdowns}"
                )

        else:

            if self.breakdowns != [] or self.action_breakdowns != []:
                raise ClickException(
                    "Wrong query. Facebook Object Node queries do not accept Breakdowns nor Action Breakdowns."
                )

            if self.level not in ["campaign", "adset", "ad"] and (
                (self.start_date and self.end_date) or self.date_preset
            ):
                raise ClickException(
                    "Wrong query. Facebook Object Node queries only accept the time_range\
                    and date_preset parameters at the 'campaign', 'adset' or 'ad' levels."
                )

            if self.time_increment:
                raise ClickException(
                    "Wrong query. Facebook Object Node queries do not accept the time_increment parameter."
                )

    def get_params(self):
        """
        Build the request parameters that will be sent to the API:
        - If AdInsights query: breakdown, action_breakdowns, level, time_range and date_preset
        - If Facebook Object Node query at the campaign, adset or ad level: time_range and date_preset
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
        - time_increment: available in AdInsights queries
        - time_range and date_preset: available in AdInsights queries,
        and in Facebook Object Node queries at the campaign, adset or ad levels only
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
        return {
            "since": self.start_date.strftime(DATEFORMAT),
            "until": self.end_date.strftime(DATEFORMAT),
        }

    def create_object(self, object_id):
        """
        Create a Facebook object based on the provided object_type and object_id.
        """
        if self.object_type == "account":
            object_id = "act_" + object_id
        obj = OBJECT_CREATION_MAPPING[self.object_type](object_id)

        return obj

    @retry
    def query_ad_insights(self, fields, params, object_id):
        """
        AdInsights documentation:
        https://developers.facebook.com/docs/marketing-api/insights
        """
        # Step 1 - Create Facebook object
        obj = self.create_object(object_id)

        # Step 2 - Run AdInsights query on Facebook object
        for element in obj.get_insights(fields=fields, params=params):
            yield element

    @retry
    def query_object_node(self, fields, params, object_id):
        """
        Supported Facebook Object Nodes: AdAccount, Campaign, AdSet, Ad and AdCreative
        Documentation: https://developers.facebook.com/docs/marketing-api/reference/
        """
        # Step 1 - Create Facebook object
        obj = self.create_object(object_id)

        # Step 2 - Run Facebook Object Node query on the Facebook object itself,
        # or on one of its edges (depending on the specified level)
        if self.level == self.object_type:
            yield obj.api_get(fields=fields, params=params)
        else:
            EDGE_QUERY_MAPPING = {
                "campaign": obj.get_campaigns(),
                "adset": obj.get_ad_sets(),
                "ad": obj.get_ads(),
                "creative": obj.get_ad_creatives(),
            }
            edge_objs = EDGE_QUERY_MAPPING[self.level]
            for element in [
                edge_obj.api_get(fields=fields, params=params) for edge_obj in edge_objs
            ]:
                yield element

    def format_and_yield(self, record):
        """
        Parse a single record into an {item: value} dictionnary.
        """
        report = {}

        for field_path in self._field_paths:
            field_values = get_field_values(
                record, field_path, self.action_breakdowns, visited=[]
            )
            if field_values:
                report.update(field_values)

        if self.add_date_to_report:
            report["date"] = datetime.today().strftime(DATEFORMAT)

        yield report

    def result_generator(self, data):
        """
        Parse all records into an {item: value} dictionnary.
        """
        for record in data:
            yield from self.format_and_yield(record.export_all_data())

    def get_data_for_object(self, object_id):
        """
        Run an API query (AdInsights or Facebook Object Node) on a single object_id.
        """
        params = self.get_params()

        if self.ad_insights:
            data = self.query_ad_insights(self._api_fields, params, object_id)
        else:
            data = self.query_object_node(self._api_fields, params, object_id)

        yield from self.result_generator(data)

    def get_data(self):
        """
        Run API queries on all object_ids.
        """
        for object_id in self.object_ids:
            yield from self.get_data_for_object(object_id)

    def read(self):

        FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
        yield NormalizedJSONStream(
            "results_" + self.object_type + "_" + "_".join(self.object_ids),
            self.get_data(),
        )
