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

from itertools import chain
from click import ClickException
from datetime import datetime

from nck.readers.reader import Reader
from nck.utils.args import extract_args
from nck.commands.command import processor
from nck.utils.retry import retry
from nck.streams.normalized_json_stream import NormalizedJSONStream
from nck.helpers.facebook_helper import (
    AD_OBJECT_TYPES,
    BREAKDOWNS_POSSIBLE_VALUES,
    LEVELS_POSSIBLE_VALUES,
    DATE_PRESETS,
    DESIRED_FIELDS,
    get_field_value,
)

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.campaign import Campaign

DATEFORMAT = "%Y-%m-%d"


def check_object_id(ctx, param, values):
    try:
        [int(value) for value in values]
        return values
    except ValueError:
        raise ClickException("Wrong format. Account ID should only contains digits")


@click.command(name="read_facebook")
@click.option("--facebook-app-id", default="", help="Not mandatory for AdsInsights reporting if access-token provided")
@click.option(
    "--facebook-app-secret", default="", help="Not mandatory for AdsInsights reporting if access-token provided"
)
@click.option("--facebook-access-token", required=True)
@click.option("--facebook-ad-object-id", required=True, multiple=True, callback=check_object_id)
@click.option("--facebook-ad-object-type", type=click.Choice(AD_OBJECT_TYPES), default=AD_OBJECT_TYPES[0])
@click.option(
    "--facebook-breakdown",
    multiple=True,
    type=click.Choice(BREAKDOWNS_POSSIBLE_VALUES),
    help="https://developers.facebook.com/docs/marketing-api/insights/breakdowns/",
)
# At this time, the Facebook connector only handle the action-breakdown "action_type"
@click.option(
    "--facebook-action-breakdown",
    multiple=True,
    type=click.Choice("action_type"),
    default=["action_type"],
    help="https://developers.facebook.com/docs/marketing-api/insights/breakdowns#actionsbreakdown",
)
@click.option(
    "--facebook-ad-insights",
    type=click.BOOL,
    default=True,
    help="https://developers.facebook.com/docs/marketing-api/insights",
)
@click.option(
    "--facebook-level",
    type=click.Choice(LEVELS_POSSIBLE_VALUES),
    default=LEVELS_POSSIBLE_VALUES[0],
    help="Represents the granularity of result",
)
@click.option("--facebook-time-increment")
@click.option("--facebook-field", multiple=True, help="Facebook API fields for the request")
@click.option(
    "--facebook-desired-field",
    multiple=True,
    type=click.Choice(list(DESIRED_FIELDS.keys())),
    help="Desired fields to get in the output report."
    "https://developers.facebook.com/docs/marketing-api/insights/parameters/v5.0#fields",
)
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
def facebook_marketing(**kwargs):
    # Should add later all the check restrictions on fields/parameters/breakdowns of the API following the value of
    # object type, see more on :
    # ---https://developers.facebook.com/docs/marketing-api/insights/breakdowns
    # ---https://developers.facebook.com/docs/marketing-api/insights
    return FacebookMarketingReader(**extract_args("facebook_", kwargs))


class FacebookMarketingReader(Reader):
    def __init__(
        self,
        app_id,
        app_secret,
        access_token,
        ad_object_id,
        ad_object_type,
        breakdown,
        action_breakdown,
        ad_insights,
        level,
        time_increment,
        field,
        desired_field,
        start_date,
        end_date,
        date_preset,
        add_date_to_report,
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.ad_object_ids = ad_object_id
        self.ad_object_type = ad_object_type
        self.breakdowns = list(breakdown)
        self.action_breakdowns = list(action_breakdown)
        self.ad_insights = ad_insights
        self.level = level
        self.time_increment = time_increment or False
        self.fields = list(field)
        self.desired_fields = list(desired_field)
        self.start_date = start_date
        self.end_date = end_date
        self.date_preset = date_preset
        self.add_date_to_report = add_date_to_report

    @retry
    def run_query_on_fb_account_obj(self, params, ad_object_id):
        account = AdAccount("act_" + ad_object_id)
        for el in account.get_insights(params=params):
            yield el

    @retry
    def run_query_on_fb_account_obj_conf(self, params, ad_object_id):
        if ad_object_id.startswith("act_"):
            raise ClickException("Wrong format. Account ID should only contains digits")
        account = AdAccount("act_" + ad_object_id)
        campaigns = account.get_campaigns()
        for el in chain(
            *[self.run_query_on_fb_campaign_obj_conf(params, campaign.get("id")) for campaign in campaigns]
        ):
            yield el

    @retry
    def run_query_on_fb_campaign_obj_conf(self, params, ad_object_id):
        campaign = Campaign(ad_object_id)
        if self.level == LEVELS_POSSIBLE_VALUES[2]:
            val_cmp = campaign.api_get(fields=self.desired_fields, params=params)
            yield val_cmp

        elif self.level == LEVELS_POSSIBLE_VALUES[1]:
            for el in chain(
                *[self.run_query_on_fb_adset_obj_conf(params, adset.get("id")) for adset in campaign.get_ad_sets()]
            ):
                yield el
        else:
            raise ClickException(
                "Received level: " + self.level + ". Available levels are " + repr(LEVELS_POSSIBLE_VALUES[1:3])
            )

    @retry
    def run_query_on_fb_adset_obj_conf(self, params, ad_object_id, level):
        adset = AdSet(ad_object_id)
        if level == LEVELS_POSSIBLE_VALUES[1]:
            val_adset = adset.api_get(fields=self.desired_fields, params=params)
            yield val_adset
        else:
            raise ClickException("Adset setup is available at 'adset' level. Received level: " + self.level)

    def get_params(self):
        params = {
            "action_breakdowns": self.action_breakdowns,
            "fields": self.fields,
            "breakdowns": self.breakdowns,
            "level": self.level,
        }
        self.add_period_to_parameters(params)
        return params

    def add_period_to_parameters(self, params):
        if self.time_increment:
            params["time_increment"] = self.time_increment
        if self.start_date and self.end_date:
            logging.info("Date format used for request : start_date and end_date")
            params["time_range"] = self.create_time_range(self.start_date, self.end_date)
        elif self.date_preset:
            logging.info("Date format used for request : date_preset")
            params["date_preset"] = self.date_preset
        else:
            logging.warning("No date range provided - Last 30 days by default")
            logging.warning(
                "https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights#parameters"
            )

    @staticmethod
    def create_time_range(start_date, end_date):
        return {"since": start_date.strftime(DATEFORMAT), "until": end_date.strftime(DATEFORMAT)}

    def format_and_yield(self, record):
        report = {field: get_field_value(record, field) for field in self.desired_fields}
        if self.add_date_to_report:
            report["date"] = datetime.today().strftime(DATEFORMAT)
        yield report

    def result_generator(self, data):
        for record in data:
            yield from self.format_and_yield(record.export_all_data())

    def get_data(self):
        for object_id in self.ad_object_ids:
            yield from self.get_data_for_object(object_id)

    def get_data_for_object(self, ad_object_id):
        params = self.get_params()
        if self.ad_insights:
            query_mapping = {AD_OBJECT_TYPES[0]: self.run_query_on_fb_account_obj}
        else:
            query_mapping = {
                AD_OBJECT_TYPES[0]: self.run_query_on_fb_account_obj_conf,
                AD_OBJECT_TYPES[1]: self.run_query_on_fb_campaign_obj_conf,
                AD_OBJECT_TYPES[2]: self.run_query_on_fb_adset_obj_conf,
            }
        try:
            query = query_mapping[self.ad_object_type]
            data = query(params, ad_object_id)
        except KeyError:
            raise ClickException("`{}` is not a valid adObject type".format(self.ad_object_type))
        yield from self.result_generator(data)

    def read(self):
        FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
        yield NormalizedJSONStream(
            "results_" + self.ad_object_type + "_" + "_".join(self.ad_object_ids), self.get_data()
        )
