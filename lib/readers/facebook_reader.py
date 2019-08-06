import click
import datetime

from itertools import chain

from lib.readers.reader import Reader
from lib.utils.args import extract_args
from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.commands.command import processor
from lib.utils.retry import retry
from lib.streams.json_stream import JSONStream

from lib.helpers.facebook_marketing_helper import (
    AD_OBJECT_TYPES,
    BREAKDOWNS_POSSIBLE_VALUES,
    ACTION_BREAKDOWNS_POSSIBLE_VALUES,
    LEVELS_POSSIBLE_VALUES,
    CMP_POSSIBLE_VALUES,
    ADS_POSSIBLE_VALUES,
)

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adaccountuser import AdAccountUser as AdUser


@click.command(name="read_facebook_marketing")
@click.option("--facebook-marketing-app-id", required=True)
@click.option("--facebook-marketing-app-secret", required=True)
@click.option("--facebook-marketing-access-token", required=True)
@click.option("--facebook-marketing-ad-object-id", required=True)
@click.option(
    "--facebook-marketing-ad-object-type",
    default="ad_account_object",
    type=click.Choice(AD_OBJECT_TYPES),
)
@click.option(
    "--facebook-marketing-breakdown",
    default=[],
    multiple=True,
    type=click.Choice(BREAKDOWNS_POSSIBLE_VALUES),
)
@click.option(
    "--facebook-marketing-action-breakdown",
    multiple=True,
    type=click.Choice(ACTION_BREAKDOWNS_POSSIBLE_VALUES),
)
@click.option("--facebook-marketing-ad-insights", default=True)
@click.option(
    "--facebook-marketing-ad-level", type=click.Choice(LEVELS_POSSIBLE_VALUES)
)
@click.option("--facebook-marketing-time-increment", default=1)
@click.option("--facebook-marketing-field", default=[], multiple=True)
@click.option("--facebook-marketing-recurse-level", default=0)
@click.option("--facebook-marketing-time-range", nargs=2, type=click.DateTime())
@click.option(
    "--facebook-marketing-day-range",
    type=click.Choice(["PREVIOUS_DAY", "LAST_30_DAYS", "LAST_7_DAYS", "LAST_90_DAYS"]),
    default=None,
)
@processor()
def facebook_marketing(**kwargs):
    # Should add later all the check restrictions on fields/parameters/breakdowns of the API following the value of
    # object type, see more on :
    # ---https://developers.facebook.com/docs/marketing-api/insights/breakdowns
    # ---https://developers.facebook.com/docs/marketing-api/insights
    return FacebookMarketingReader(**extract_args("facebook_marketing_", kwargs))


class FacebookMarketingReader(Reader):
    def __init__(
        self, app_id, app_secret, access_token, ad_object_id, ad_object_type, **kwargs
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.ad_object_id = ad_object_id
        self.ad_object_type = ad_object_type
        self.kwargs = kwargs

    @retry
    def run_query_on_fb_user_obj(self, params, ad_object_id, recurse_level):
        user = AdUser(fbid=ad_object_id)
        accounts = user.get_ad_accounts()
        for el in chain(
            *[
                self.run_query_on_fb_account_obj(
                    params, account.get("id"), recurse_level - 1
                )
                for account in accounts
            ]
        ):
            yield el

    @retry
    def run_query_on_fb_account_obj(self, params, ad_object_id, recurse_level):
        account = AdAccount("act_" + ad_object_id)
        campaigns = account.get_campaigns()
        if recurse_level <= 0:
            for el in account.get_insights(params=params):
                yield el
        else:
            for el in chain(
                *[
                    self.run_query_on_fb_campaign_obj(
                        params, campaign.get("id"), recurse_level - 1
                    )
                    for campaign in campaigns
                ]
            ):
                yield el

    @retry
    def run_query_on_fb_campaign_obj(self, params, ad_object_id, recurse_level):
        campaign = Campaign(ad_object_id)
        if recurse_level <= 0:
            for el in campaign.get_insights(params=params):
                yield el
        else:
            for el in chain(
                *[
                    self.run_query_on_fb_adset_obj(
                        params, adset.get("id"), recurse_level - 1
                    )
                    for adset in campaign.get_ad_sets()
                ]
            ):
                yield el

    @retry
    def run_query_on_fb_adset_obj(self, params, ad_object_id, recurse_level):
        adset = AdSet(ad_object_id)
        if recurse_level <= 0:
            for el in adset.get_insights(params=params):
                yield el
        else:
            for el in chain(
                *[
                    self.run_query_on_fb_ad_obj(params, ad.get("id"))
                    for ad in adset.get_ads()
                ]
            ):
                yield el

    @retry
    def run_query_on_fb_ad_obj(self, params, ad_object_id):
        ad = Ad(ad_object_id)
        for el in ad.get_insights(params):
            yield el

    @retry
    def run_query_on_fb_campaign_obj_conf(self, params, ad_object_id, recurse_level):
        campaign = Campaign(ad_object_id)

        if recurse_level <= 0:
            val_cmp = campaign.api_get(fields=CMP_POSSIBLE_VALUES, params=params)
            yield val_cmp.export_value(val_cmp._data)
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
            val_adset = adset.api_get(fields=ADS_POSSIBLE_VALUES)
            yield val_adset.export_value(val_adset._data)
        else:
            raise Exception(
                "for now, just campaign object and adset object are able to be requested without insight"
            )

    def get_days_delta(self):
        days_range = self.kwargs.get("day_range")
        if days_range == "PREVIOUS_DAY":
            days_delta = 1
        elif days_range == "LAST_7_DAYS":
            days_delta = 7
        elif days_range == "LAST_30_DAYS":
            days_delta = 30
        elif days_range == "LAST_90_DAYS":
            days_delta = 90
        else:
            raise Exception("{} is not handled by the reader".format(days_range))
        return days_delta

    def get_params(self):

        params = {
            "action_breakdowns": self.kwargs.get("action_breakdown", []),
            "fields": self.kwargs.get("field", []),
            "breakdowns": self.kwargs.get("breakdown", []),
            "time_increment": self.kwargs.get("time_increment", 1),
        }

        if "ad_level" in self.kwargs:
            params["level"] = self.kwargs["ad_level"]

        if self.kwargs.get("time_range"):
            date_start, date_stop = self.kwargs.get("time_range")
            params["time_range"] = {
                "since": date_start.strftime("%Y-%m-%d"),
                "until": date_stop.strftime("%Y-%m-%d"),
            }
        elif self.kwargs.get("day_range"):
            date_stop = datetime.datetime.now().date()
            days_delta = self.get_days_delta()
            date_start = date_stop - datetime.timedelta(days=days_delta)
            params["time_range"] = {
                "since": date_start.strftime("%Y-%m-%d"),
                "until": date_stop.strftime("%Y-%m-%d"),
            }
        return params

    def read(self):

        FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
        params = self.get_params()
        object_type = self.ad_object_type
        recurse_level = self.kwargs.get("recurse_level")

        if self.kwargs.get("ad_insights", True):
            if object_type == "ad_account_object":
                data = self.run_query_on_fb_account_obj(
                    params, self.ad_object_id, recurse_level
                )
            elif object_type == "ad_campaign_object":
                data = self.run_query_on_fb_campaign_obj(
                    params, self.ad_object_id, recurse_level
                )
            elif object_type == "adset_object":
                data = self.run_query_on_fb_adset_obj(
                    params, self.ad_object_id, recurse_level
                )
            elif object_type == "ad_object":
                data = self.run_query_on_fb_ad_obj(params, self.ad_object_id)
        else:
            if object_type == "ad_campaign_object":
                data = self.run_query_on_fb_campaign_obj_conf(
                    params, self.ad_object_id, recurse_level
                )
            elif object_type == "ad_adset_object":
                data = self.run_query_on_fb_adset_obj_conf(
                    params, self.ad_object_id, recurse_level
                )
            else:
                raise Exception(
                    "For now only [campaign, adset] objects type can be requested without insight"
                )

        def result_generator():
            for record in data:
                yield record.export_data()

        yield JSONStream(
            "results_" + object_type + "_" + str(self.ad_object_id), result_generator()
        )
