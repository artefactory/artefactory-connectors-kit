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
from typing import List, Tuple, Literal

from pydantic import BaseModel, validator

GOOGLE_TOKEN_URI = "https://accounts.google.com/o/oauth2/token"
DISCOVERY_URI = "https://analyticsreporting.googleapis.com/$discovery/rest"
DATEFORMAT = "%Y-%m-%d"
DAY_RANGES = ("PREVIOUS_DAY", "LAST_30_DAYS", "LAST_7_DAYS", "LAST_90_DAYS")
SAMPLING_LEVELS = ("SMALL", "DEFAULT", "LARGE")

PREFIX = "^ga:"


class GoogleAnalyticsReaderConfig(BaseModel):
    access_token: str = None
    refresh_token: str
    client_id: str
    client_secret: str
    view_id: List[str] = [""]
    account_id: List[str] = []
    dimension: List[str] = []
    metric: List[str] = []
    segment_id: List[str] = []
    start_date: datetime = None
    end_date: datetime = None
    date_range: Tuple[datetime, datetime] = None
    day_range: Literal[DAY_RANGES] = None
    sampling_level: Literal[SAMPLING_LEVELS] = "LARGE"
    add_view: bool = False

    @validator("start_date", "end_date", pre=True)
    def date_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Datetime format must follow 'YYYY-MM-DD'")
        return v
