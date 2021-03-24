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
from typing import Literal

from pydantic import BaseModel, validator

from nck.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS

LIMIT_REQUEST_MYTARGET = 20

REQUEST_TYPES = ["performance", "budget"]

REQUEST_CONFIG = {
    "refresh_agency_token": {
        "url": "https://target.my.com/api/v2/oauth2/token.json",
        "headers_type": "content_type",
        "offset": False,
        "_campaign_id": False,
        "dates_required": False,
        "ids": False,
    },
    "get_campaign_ids_names": {
        "url": "https://target.my.com/api/v2/campaigns.json?fields=id,name",
        "headers_type": "authorization",
        "offset": True,
        "_campaign_id": False,
        "dates_required": False,
        "ids": False,
    },
    "get_banner_ids_names": {
        "url": "https://target.my.com/api/v2/banners.json?fields=id,name,campaign_id",
        "headers_type": "authorization",
        "offset": True,
        "_campaign_id": False,
        "dates_required": False,
        "ids": False,
    },
    "get_banner_stats": {
        "url": "https://target.my.com/api/v2/statistics/banners/day.json",
        "headers_type": "authorization",
        "offset": False,
        "_campaign_id": False,
        "dates_required": True,
        "ids": False,
    },
    "get_campaign_budgets": {
        "url": "https://target.my.com/api/v2/campaigns.json?fields=id,name,budget_limit,budget_limit_day",
        "headers_type": "authorization",
        "offset": True,
        "_campaign_id": False,
        "dates_required": False,
        "ids": False,
    },
    "get_campaign_dates": {
        "url": "https://target.my.com/api/v2/campaigns.json?fields=id,name,date_start,date_end,status",
        "headers_type": "authorization",
        "offset": True,
        "_campaign_id": False,
        "dates_required": False,
        "ids": False,
    },
}


class MyTargetReaderConfig(BaseModel):
    client_id: str
    client_secret: str
    refresh_token: str
    request_type: Literal[tuple(REQUEST_TYPES)]
    date_range: Literal[tuple(DEFAULT_DATE_RANGE_FUNCTIONS.keys())] = None
    start_date: datetime = None
    end_date: datetime = None

    @validator("start_date", "end_date", pre=True)
    def date_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Datetime format must follow 'YYYY-MM-DD'")
        return v
