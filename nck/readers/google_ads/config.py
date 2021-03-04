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

DATEFORMAT = "%Y%m%d"
ENCODING = "utf-8"

# https://developers.google.com/adwords/api/docs/appendix/reports#available-reports
REPORT_TYPE_POSSIBLE_VALUES = [
    "KEYWORDS_PERFORMANCE_REPORT",
    "AD_PERFORMANCE_REPORT",
    "URL_PERFORMANCE_REPORT",
    "ADGROUP_PERFORMANCE_REPORT",
    "CAMPAIGN_PERFORMANCE_REPORT",
    "ACCOUNT_PERFORMANCE_REPORT",
    "GEO_PERFORMANCE_REPORT",
    "SEARCH_QUERY_PERFORMANCE_REPORT",
    "AUTOMATIC_PLACEMENTS_PERFORMANCE_REPORT",
    "CAMPAIGN_NEGATIVE_KEYWORDS_PERFORMANCE_REPORT",
    "CAMPAIGN_NEGATIVE_PLACEMENTS_PERFORMANCE_REPORT",
    "SHARED_SET_REPORT",
    "CAMPAIGN_SHARED_SET_REPORT",
    "SHARED_SET_CRITERIA_REPORT",
    "CREATIVE_CONVERSION_REPORT",
    "CALL_METRICS_CALL_DETAILS_REPORT",
    "KEYWORDLESS_QUERY_REPORT",
    "KEYWORDLESS_CATEGORY_REPORT",
    "CRITERIA_PERFORMANCE_REPORT",
    "CLICK_PERFORMANCE_REPORT",
    "BUDGET_PERFORMANCE_REPORT",
    "BID_GOAL_PERFORMANCE_REPORT",
    "DISPLAY_KEYWORD_PERFORMANCE_REPORT",
    "PLACEHOLDER_FEED_ITEM_REPORT",
    "PLACEMENT_PERFORMANCE_REPORT",
    "CAMPAIGN_NEGATIVE_LOCATIONS_REPORT",
    "GENDER_PERFORMANCE_REPORT",
    "AGE_RANGE_PERFORMANCE_REPORT",
    "CAMPAIGN_LOCATION_TARGET_REPORT",
    "CAMPAIGN_AD_SCHEDULE_TARGET_REPORT",
    "PAID_ORGANIC_QUERY_REPORT",
    "AUDIENCE_PERFORMANCE_REPORT",
    "DISPLAY_TOPICS_PERFORMANCE_REPORT",
    "USER_AD_DISTANCE_REPORT",
    "SHOPPING_PERFORMANCE_REPORT",
    "PRODUCT_PARTITION_REPORT",
    "PARENTAL_STATUS_PERFORMANCE_REPORT",
    "PLACEHOLDER_REPORT",
    "AD_CUSTOMIZERS_FEED_ITEM_REPORT",
    "LABEL_REPORT",
    "FINAL_URL_REPORT",
    "VIDEO_PERFORMANCE_REPORT",
    "TOP_CONTENT_PERFORMANCE_REPORT",
    "CAMPAIGN_CRITERIA_REPORT",
    "CAMPAIGN_GROUP_PERFORMANCE_REPORT",
    "LANDING_PAGE_REPORT",
    "MARKETPLACE_PERFORMANCE_REPORT",
]

# https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges
DATE_RANGE_TYPE_POSSIBLE_VALUES = [
    "YESTERDAY",
    "TODAY",
    "LAST_7_DAYS",
    "LAST_WEEK",
    "LAST_BUSINESS_WEEK",
    "THIS_MONTH",
    "LAST_MONTH",
    "ALL_TIME",
    "LAST_14_DAYS",
    "LAST_30_DAYS",
    "THIS_WEEK_SUN_TODAY",
    "THIS_WEEK_MON_TODAY",
    "LAST_WEEK_SUN_SAT",
    "CUSTOM_DATE",
]
