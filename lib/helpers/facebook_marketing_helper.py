from facebook_business.adobjects.adsinsights import AdsInsights

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
