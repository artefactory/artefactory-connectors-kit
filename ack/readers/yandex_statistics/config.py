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
import random
import datetime
from typing import Literal, List, Tuple

from pydantic import BaseModel, validator

YANDEX_DIRECT_API_BASE_URL = "https://api.direct.yandex.com/json/v5/"

LANGUAGES = ["en", "ru", "uk"]

REPORT_TYPES = [
    "ACCOUNT_PERFORMANCE_REPORT",
    "CAMPAIGN_PERFORMANCE_REPORT",
    "ADGROUP_PERFORMANCE_REPORT",
    "AD_PERFORMANCE_REPORT",
    "CRITERIA_PERFORMANCE_REPORT",
    "CUSTOM_REPORT",
    "REACH_AND_FREQUENCY_PERFORMANCE_REPORT",
    "SEARCH_QUERY_PERFORMANCE_REPORT",
]

STATS_FIELDS = [
    "AdFormat",
    "AdGroupId",
    "AdGroupName",
    "AdId",
    "AdNetworkType",
    "Age",
    "AudienceTargetId",
    "AvgClickPosition",
    "AvgCpc",
    "AvgCpm",
    "AvgImpressionFrequency",
    "AvgImpressionPosition",
    "AvgPageviews",
    "AvgTrafficVolume",
    "BounceRate",
    "Bounces",
    "CampaignId",
    "CampaignName",
    "CampaignType",
    "CarrierType",
    "Clicks",
    "ClickType",
    "ConversionRate",
    "Conversions",
    "Cost",
    "CostPerConversion",
    "Criteria",
    "CriteriaId",
    "CriteriaType",
    "Criterion",
    "CriterionId",
    "CriterionType",
    "Ctr",
    "Date",
    "Device",
    "DynamicTextAdTargetId",
    "ExternalNetworkName",
    "Gender",
    "GoalsRoi",
    "ImpressionReach",
    "Impressions",
    "ImpressionShare",
    "Keyword",
    "LocationOfPresenceId",
    "LocationOfPresenceName",
    "MatchedKeyword",
    "MatchType",
    "MobilePlatform",
    "Month",
    "Placement",
    "Profit",
    "Quarter",
    "Query",
    "Revenue",
    "RlAdjustmentId",
    "Sessions",
    "Slot",
    "SmartBannerFilterId",
    "TargetingLocationId",
    "TargetingLocationName",
    "Week",
    "WeightedCtr",
    "WeightedImpressions",
    "Year",
]

DATE_RANGE_TYPES = [
    "TODAY",
    "YESTERDAY",
    "THIS_WEEK_MON_TODAY",
    "THIS_WEEK_SUN_TODAY",
    "LAST_WEEK",
    "LAST_BUSINESS_WEEK",
    "LAST_WEEK_SUN_SAT",
    "THIS_MONTH",
    "LAST_MONTH",
    "ALL_TIME",
    "CUSTOM_DATE",
    "AUT0",
    "LAST_3_DAYS",
    "LAST_5_DAYS",
    "LAST_7_DAYS",
    "LAST_14_DAYS",
    "LAST_30_DAYS",
    "LAST_90_DAYS",
    "LAST_365_DAYS",
]

OPERATORS = [
    "EQUALS",
    "NOT_EQUALS",
    "IN",
    "NOT_IN",
    "LESS_THAN",
    "GREATER_THAN",
    "STARTS_WITH_IGNORE_CASE",
    "DOES_NOT_START_WITH_IGNORE_CASE",
    "STARTS_WITH_ANY_IGNORE_CASE",
    "DOES_NOT_START_WITH_ALL_IGNORE_CASE",
]


class YandexStatisticsReaderConfig(BaseModel):
    token: str
    report_language: Literal[tuple(LANGUAGES)] = "en"
    filters: List[Tuple[Literal[tuple(STATS_FIELDS)], Literal[tuple(OPERATORS)], str]] = []
    max_rows: int = None
    fields: List[Literal[tuple(STATS_FIELDS)]]
    report_name: str = f"stats_report_{datetime.date.today()}_{random.randrange(10000)}"
    report_type: Literal[tuple(REPORT_TYPES)]
    date_range: Literal[tuple(DATE_RANGE_TYPES)]
    include_vat: bool
    date_start: datetime.datetime = None
    date_stop: datetime.datetime = None

    @validator("date_start", "date_stop", pre=True)
    def date_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Datetime format must follow 'YYYY-MM-DD'")
        return v

    @validator("filters")
    def filters_str_to_list(cls, v):
        for i in range(len(v)):
            v[i] = list(v[i])
            v[i][2] = v[i][2].split(",")
        return v
