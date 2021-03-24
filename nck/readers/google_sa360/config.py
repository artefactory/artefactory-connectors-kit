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

from pydantic import BaseModel, validator

from nck.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS

REPORT_TYPES = [
    "advertiser",
    "account",
    "ad",
    "adGroup",
    "adGroupTarget",
    "bidStrategy",
    "campaign",
    "campaignTarget",
    "conversion",
    "feedltem",
    "floodlightActivity",
    "keyword",
    "negativeAdGroupKeyword",
    "negativeAdGroupTarget",
    "negativeCampaignKeyword",
    "negativeCampaignTarget",
    "paidAndOrganic",
    "productAdvertised",
    "productGroup",
    "productLeadAndCrossSell",
    "productTarget",
    "visit",
]


class GoogleSA360ReaderConfig(BaseModel):
    access_token: str = None
    refresh_token: str
    client_id: str
    client_secret: str
    agency_id: str
    advertiser_ids: List[str] = []
    report_name: str = "SA360 Report"
    report_type: Literal[tuple(REPORT_TYPES)] = REPORT_TYPES[0]
    columns: List[str] = []
    saved_columns: List[str] = []
    start_date: datetime = None
    end_date: datetime = None
    date_range: Literal[tuple(DEFAULT_DATE_RANGE_FUNCTIONS.keys())] = None

    @validator("start_date", "end_date", pre=True)
    def date_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Datetime format must follow 'YYYY-MM-DD'")
        return v
