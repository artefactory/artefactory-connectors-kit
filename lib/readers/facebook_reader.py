import logging
import click

from itertools import chain
from click import ClickException

from lib.readers.reader import Reader
from lib.utils.args import extract_args
from lib.commands.command import processor
from lib.utils.retry import retry
from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.helpers.facebook_helper import (
    AD_OBJECT_TYPES,
    BREAKDOWNS_POSSIBLE_VALUES,
    LEVELS_POSSIBLE_VALUES,
    CMP_POSSIBLE_VALUES,
    ADS_POSSIBLE_VALUES,
    DATE_PRESETS,
    DESIRED_FIELDS,
    get_field_value,
)

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.campaign import Campaign

DATEFORMAT = "%Y-%m-%d"


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
@click.option("--facebook-ad-object-id", required=True)
@click.option(
    "--facebook-ad-object-type",
    type=click.Choice(AD_OBJECT_TYPES),
    default=AD_OBJECT_TYPES[0],
)
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
    "--facebook-ad-level",
    type=click.Choice(LEVELS_POSSIBLE_VALUES),
    default=LEVELS_POSSIBLE_VALUES[0],
    help="Granularity of insights",
)
@click.option("--facebook-time-increment")
@click.option(
    "--facebook-field", multiple=True, help="Facebook API fields for the request"
)
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
@click.option("--facebook-recurse-level", default=0)
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
        ad_level,
        time_increment,
        field,
        desired_field,
        start_date,
        end_date,
        date_preset,
        recurse_level,
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.ad_object_id = ad_object_id
        self.ad_object_type = ad_object_type
        self.breakdowns = list(breakdown)
        self.action_breakdowns = list(action_breakdown)
        self.ad_insights = ad_insights
        self.ad_level = ad_level
        self.time_increment = time_increment or False
        self.fields = list(field)
        self.desired_fields = list(desired_field)
        self.start_date = start_date
        self.end_date = end_date
        self.date_preset = date_preset
        self.recurse_level = recurse_level

    @retry
    def run_query_on_fb_account_obj(self, params, ad_object_id):
        if ad_object_id.startswith("act_"):
            raise ClickException("Wrong format. Account ID should only contains digits")
        account = AdAccount("act_" + ad_object_id)
        for el in account.get_insights(params=params):
            yield el

    @retry
    def run_query_on_fb_campaign_obj_conf(self, params, ad_object_id, recurse_level):
        campaign = Campaign(ad_object_id)
        if recurse_level <= 0:
            val_cmp = campaign.api_get(fields=CMP_POSSIBLE_VALUES, params=params)
            yield val_cmp

        else:
            for el in chain(
                *[
                    self.run_query_on_fb_adset_obj_conf(
                        params, adset.get("id"), recurse_level - 1
                    )
                    for adset in campaign.get_ad_sets()
                ]
            ):
                yield el

    @retry
    def run_query_on_fb_adset_obj_conf(self, params, ad_object_id, recurse_level):
        adset = AdSet(ad_object_id)
        if recurse_level <= 0:
            val_adset = adset.api_get(fields=ADS_POSSIBLE_VALUES, params=params)
            yield val_adset
        else:
            raise ClickException(
                "for now, just campaign object and adset object are able to be requested without insights"
            )

    def get_params(self):
        params = {
            "action_breakdowns": self.action_breakdowns,
            "fields": self.fields,
            "breakdowns": self.breakdowns,
            "level": self.ad_level,
        }
        self.add_period_to_parameters(params)
        return params

    def add_period_to_parameters(self, params):
        if self.time_increment:
            params["time_increment"] = self.time_increment
        if self.start_date and self.end_date:
            logging.info("ℹ️ Date format used for request : start_date and end_date")
            params["time_range"] = self.create_time_range(
                self.start_date, self.end_date
            )
        elif self.date_preset:
            logging.info("ℹ️ Date format used for request : date_preset")
            params["date_preset"] = self.date_preset
        else:
            logging.warning("⚠️ No date range provided - Last 30 days by default ⚠️")
            logging.warning(
                "https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights#parameters"
            )

    @staticmethod
    def create_time_range(start_date, end_date):
        return {
            "since": start_date.strftime(DATEFORMAT),
            "until": end_date.strftime(DATEFORMAT),
        }

    def format_and_yield(self, record):
        yield {field: get_field_value(record, field) for field in self.desired_fields}

    def result_generator(self, data):
        for record in data:
            yield from self.format_and_yield(record.export_all_data())

    def read(self):
        FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
        params = self.get_params()

        if self.ad_insights:
            query_mapping = {AD_OBJECT_TYPES[0]: self.run_query_on_fb_account_obj}
            args = [params, self.ad_object_id]
        else:
            query_mapping = {
                AD_OBJECT_TYPES[1]: self.run_query_on_fb_campaign_obj_conf,
                AD_OBJECT_TYPES[2]: self.run_query_on_fb_adset_obj_conf,
            }
            args = [params, self.ad_object_id, self.recurse_level]
        try:
            query = query_mapping[self.ad_object_type]
            data = query(*args)
        except KeyError:
            raise ClickException(
                "`{}` is not a valid adObject type".format(self.ad_object_type)
            )

        yield NormalizedJSONStream(
            "results_" + self.ad_object_type + "_" + str(self.ad_object_id),
            self.result_generator(data),
        )
