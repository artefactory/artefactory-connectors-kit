from facebook_business.adobjects.adsinsights import AdsInsights

BREAKDOWNS_POSSIBLE_VALUES = [v for k, v in AdsInsights.Breakdowns.__dict__.items() if not k.startswith("__")]

ACTION_BREAKDOWNS_POSSIBLE_VALUES = [
    v for k, v in AdsInsights.ActionBreakdowns.__dict__.items() if not k.startswith("__")
]

AD_OBJECT_TYPES = ["adaccount", "campaign", "adset", "ad", "user"]

LEVELS_POSSIBLE_VALUES = ["ad", "adset", "campaign", "account"]

CMP_POSSIBLE_VALUES = [
    "account_id",
    "adlabels",
    "bid_strategy",
    "boosted_object_id",
    "brand_lift_studies",
    "budget_rebalance_flag",
    "budget_remaining",
    "buying_type",
    "can_create_brand_lift_study",
    "can_use_spend_cap",
    "configured_status",
    "created_time",
    "daily_budget",
    "effective_status",
    "id",
    "issues_info",
    "last_budget_toggling_time",
    "lifetime_budget",
    "name",
    "objective",
    "pacing_type",
    "promoted_object",
    "recommendations",
    "source_campaign",
    "source_campaign_id",
    "spend_cap",
    "start_time",
    "status",
    "stop_time",
    "topline_id",
    "updated_time",
]

# should have done this list comprehension selection but
# some of the fields are obsolet and doesn't work, i took the most important
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

DATE_PRESETS = [v for k, v in AdsInsights.DatePreset.__dict__.items() if not k.startswith("__")]
