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
from typing import List, Literal

from twitter_ads.campaign import Campaign, FundingInstrument, LineItem
from twitter_ads.creative import CardsFetch, MediaCreative, PromotedTweet
from pydantic import BaseModel, validator
from datetime import datetime

from ack.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS

API_DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"
REP_DATEFORMAT = "%Y-%m-%d"
MAX_WAITING_SEC = 3600
MAX_ENTITY_IDS_PER_JOB = 20
MAX_CONCURRENT_JOBS = 100

REPORT_TYPES = ["ANALYTICS", "REACH", "ENTITY"]

ENTITY_OBJECTS = {
    "FUNDING_INSTRUMENT": FundingInstrument,
    "CAMPAIGN": Campaign,
    "LINE_ITEM": LineItem,
    "MEDIA_CREATIVE": MediaCreative,
    "PROMOTED_TWEET": PromotedTweet,
}

ENTITY_ATTRIBUTES = {
    **{entity: list(ENTITY_OBJECTS[entity].__dict__["PROPERTIES"].keys()) for entity in ENTITY_OBJECTS},
    "CARD": list(CardsFetch.__dict__["PROPERTIES"].keys()),
}

GRANULARITIES = ["DAY", "TOTAL"]

METRIC_GROUPS = [
    "ENGAGEMENT",
    "BILLING",
    "VIDEO",
    "MEDIA",
    "MOBILE_CONVERSION",
    "WEB_CONVERSION",
    "LIFE_TIME_VALUE_MOBILE_CONVERSION",
]

PLACEMENTS = [
    "ALL_ON_TWITTER",
    "PUBLISHER_NETWORK",
]

SEGMENTATION_TYPES = [
    "AGE",
    "APP_STORE_CATEGORY",
    "AUDIENCES",
    "CONVERSATIONS",
    "CONVERSION_TAGS",
    "DEVICES",
    "EVENTS",
    "GENDER",
    "INTERESTS",
    "KEYWORDS",
    "LANGUAGES",
    "LOCATIONS",
    "METROS",
    "PLATFORMS",
    "PLATFORM_VERSIONS",
    "POSTAL_CODES",
    "REGIONS",
    "SIMILAR_TO_FOLLOWERS_OF_USER",
    "TV_SHOWS",
]


class TwitterReaderConfig(BaseModel):
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str
    account_id: str
    report_type: Literal[tuple(REPORT_TYPES)]
    entity: Literal[tuple(ENTITY_ATTRIBUTES.keys())]
    entity_attribute: List[str] = []
    granularity: Literal[tuple(GRANULARITIES)] = "TOTAL"
    metric_group: List[Literal[tuple(METRIC_GROUPS)]] = []
    placement: Literal[tuple(PLACEMENTS)] = "ALL_ON_TWITTER"
    segmentation_type: Literal[tuple(SEGMENTATION_TYPES)] = None
    platform: str = None
    country: str = None
    start_date: datetime = None
    end_date: datetime = None
    add_request_date_to_report: bool = False
    date_range: Literal[tuple(DEFAULT_DATE_RANGE_FUNCTIONS.keys())] = None

    @validator("start_date", "end_date", pre=True)
    def date_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Datetime format must follow 'YYYY-MM-DD'")
        return v
