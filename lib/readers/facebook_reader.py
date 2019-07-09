import click

from itertools import chain 

from lib.readers.reader import Reader
from lib.utils.args import extract_args
from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.commands.command import processor
from lib.utils.retry import retry
from lib.helpers.facebook_marketing_helper import AD_OBJECT_TYPES, BREAKDOWNS_POSSIBLE_VALUES, ACTION_BREAKDOWNS_POSSIBLE_VALUES

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.ad import Ad


@click.command(name="read_facebook_marketing")
@click.option("--facebook-marketing-app-id", required = True)
@click.option("--facebook-marketing-app-secret", required = True)
@click.option("--facebook-marketing-access-token", required = True)
@click.option("--facebook-marketing-ad-object-id", required = True)
@click.option("--facebook-marketing-ad-object-type", default = 'ad_account_object', type=click.Choice(AD_OBJECT_TYPES))
@click.option("--facebook-marketing-breakdown", multiple = True, type=click.Choice(BREAKDOWNS_POSSIBLE_VALUES))
@click.option("--facebook-marketing-action-breakdown", multiple = True, type=click.Choice(ACTION_BREAKDOWNS_POSSIBLE_VALUES))
@click.option("--facebook-marketing-ad-insights", default = True)
@click.option("--facebook-marketing-ad-level")
@click.option("--facebook-marketing-time-increment", default = 1)
@click.option("--facebook-marketing-ad-account-id")
@click.option("--facebook-marketing-field", multiple = True)
@click.option("--facebook-marketing-recurse-level", default = 0)
@click.option("--facebook-marketing-time-range", nargs=2, type=(click.DateTime(formats='%Y-%m-%d'), click.DateTime(formats='%Y-%m-%d')))
@processor()
def facebook_marketing(**kwargs):
    # Should add later all the check restrictions on fields/parameters/breakdowns of the API following the value of 
    # object type, see more on :
    #---https://developers.facebook.com/docs/marketing-api/insights/breakdowns
    #---https://developers.facebook.com/docs/marketing-api/insights
    return FacebookMarketingReader(**extract_args('facebook_marketing_', kwargs))


class FacebookMarketingReader(Reader):

    def __init__(self, app_id, app_secret, access_token, ad_object_id, ad_object_type, **kwargs):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.ad_object_id = ad_object_id
        self.ad_object_type = ad_object_type
        self.kwargs = kwargs

    @retry
    def run_query_on_fb_account_obj(self, params, ad_object_id, recurse_level):
        account = AdAccount('act_' + ad_object_id)
        if recurse_level <= 0 :
            for el in account.get_insights(params = params):
                yield el
        else: 
            for el in chain((self.run_query_on_fb_campaign_obj(params, campaign.get('id'), recurse_level - 1) for campaign in account.get_campaigns())):
                yield el

    @retry
    def run_query_on_fb_campaign_obj(self, params, ad_object_id, recurse_level):
        campaign = Campaign(ad_object_id)
        if recurse_level <= 0 :
            for el in campaign.get_insights(params = params):
                yield el
        else: 
            for el in chain((self.run_query_on_fb_adset_obj(params, adset.get('id'), recurse_level - 1) for adset in campaign.get_ad_sets())):
                yield el
                
    @retry
    def run_query_on_fb_adset_obj(self, params, ad_object_id, recurse_level):
        adset = AdSet(ad_object_id)
        if recurse_level <= 0 :
            for el in adset.get_insights(params = params):
                yield el
        else: 
            for el in chain((self.run_query_on_fb_ad_obj(params, ad.get('id')) for ad in adset.get_ads())):
                yield el
 

    def read(self):

        FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
        params = {
            "action_breakdowns": self.kwargs.get('facebook_marketing_action_breakdowns',[]),
            'fields':  self.kwargs.get('facebook_marketing_action_field',[]),
            'breakdowns': self.kwargs.get('facebook_marketing_breakdown',[]),
            'time_increment': self.kwargs.get('facebook_marketing_time_increment'),
        }
        
        if "facebook_marketing_ad_level" in self.kwargs:
            params['level'] = self.kwargs["facebook_marketing_ad_level"]
       
        if self.kwargs.get('facebook_marketing_ad_insights', False):
            object_type = self.kwargs.get('facebook_marketing_object_type')
            recurse_level = self.kwargs.get('facebook_marketing_recurse_level')
            if (object_type == 'ad_account_object'):

            """
        if self.ad_object_type == 'ad_account_object':

            account_obj = AdAccount('act_' + self.fb_ad_object_id)
            self.run_query_on_fb_ad_account_obj(account_obj)

        elif self.ad_object_type == 'ad_campaign_object':

            ad_campaign_obj = Campaign(self.fb_ad_object_id)
            self.run_query_on_fb_ad_campaign_obj(ad_campaign_obj)

        elif self.ad_object_type == 'ad_set_object':

            adset_obj = AdSet(self.fb_ad_object_id)
            self.run_query_on_fb_adset_obj(adset_obj)

        elif self.ad_object_type == 'ad_object':

            ad_obj = Ad(self.fb_ad_object_id)
            self.run_query_on_fb_ad_obj(ad_obj)

        for _sheet_name in self._sheet_name:

            worksheet = spreadsheet.worksheet(_sheet_name)

            def result_generator():
                for record in worksheet.get_all_records():
                    yield record

            yield NormalizedJSONStream(worksheet.title, result_generator())
"""