from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.campaign import Campaign


BREAKDOWNS_POSSIBLE_VALUES = [
    v for k, v in AdsInsights.Breakdowns.__dict__.items() if not k.startswith("__")
]

ACTION_BREAKDOWNS_POSSIBLE_VALUES = [
    v
    for k, v in AdsInsights.ActionBreakdowns.__dict__.items()
    if not k.startswith("__")
]

AD_OBJECT_TYPES = [
    "ad_account_object",
    "ad_campaign_object",
    "adset_object",
    "ad_object",
    "ad_user",
]

LEVELS_POSSIBLE_VALUES = ["ad", "adset", "campaign", "account"]

CMP_POSSIBLE_VALUES = [
    v for k, v in Campaign.Field.__dict__.items() if not k.startswith("__")
][:-4]


# should have done this list comprehension selection but, some of the fields are obsolet and doesn't work, i took the most importants
# ADS_POSSIBLE_VALUES = [v for k,v in AdSet.Field.__dict__.items() if not k.startswith("__")]

ADS_POSSIBLE_VALUES = [
    "account_id",
    "adlabels",
    "asset_feed_id",
    "budget_remaining",
    "campaign",
    "campaign_id",
    "configured_status",
    "created_time",
    "creative_sequence",
    "daily_budget",
    "end_time",
    "lifetime_budget",
    "lifetime_imps",
    "lifetime_min_spend_target",
    "lifetime_spend_cap",
    "name",
    "pacing_type",
    "source_adset",
    "source_adset_id",
    "start_time",
    "status",
]
