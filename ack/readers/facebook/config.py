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
from datetime import datetime
from typing import List, Literal

from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.adspixel import AdsPixel
from facebook_business.adobjects.campaign import Campaign
from pydantic import BaseModel, validator

DATEFORMAT = "%Y-%m-%d"
BATCH_SIZE_LIMIT = 50

FACEBOOK_OBJECTS = ["pixel", "creative", "ad", "adset", "campaign", "account"]
DATE_PRESETS = [v for k, v in AdsInsights.DatePreset.__dict__.items() if not k.startswith("__")]
BREAKDOWNS = [v for k, v in AdsInsights.Breakdowns.__dict__.items() if not k.startswith("__")]
ACTION_BREAKDOWNS = [v for k, v in AdsInsights.ActionBreakdowns.__dict__.items() if not k.startswith("__")]

OBJECT_CREATION_MAPPING = {
    "account": AdAccount,
    "campaign": Campaign,
    "adset": AdSet,
    "ad": Ad,
    "creative": AdCreative,
    "pixel": AdsPixel,
}

EDGE_MAPPING = {
    "account": ["campaign", "adset", "ad", "creative", "pixel"],
    "campaign": ["adset", "ad"],
    "adset": ["ad", "creative"],
    "ad": ["creative"],
}

EDGE_QUERY_MAPPING = {
    "campaign": lambda obj: obj.get_campaigns(),
    "adset": lambda obj: obj.get_ad_sets(),
    "ad": lambda obj: obj.get_ads(),
    "creative": lambda obj: obj.get_ad_creatives(),
    "pixel": lambda obj: obj.get_ads_pixels(),
}


class FacebookReaderConfig(BaseModel):
    app_id: str = ""
    app_secret: str = ""
    access_token: str
    object_id: List[str]
    object_type: Literal[tuple(FACEBOOK_OBJECTS)] = "account"
    level: Literal[tuple(FACEBOOK_OBJECTS)] = "ad"
    ad_insights: bool = True
    breakdown: List[Literal[tuple(BREAKDOWNS)]] = []
    action_breakdown: List[Literal[tuple(ACTION_BREAKDOWNS)]] = []
    field: List[str] = []
    time_increment: str = None
    start_date: datetime = None
    end_date: datetime = None
    date_preset: Literal[tuple(DATE_PRESETS)] = None
    add_date_to_report: bool = False

    @validator("start_date", "end_date", pre=True)
    def date_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Datetime format must follow 'YYYY-MM-DD'")
        return v
