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
from typing import List, Literal, Tuple

from pydantic import BaseModel, validator

GOOGLE_TOKEN_URI = "https://accounts.google.com/o/oauth2/token"

DAY_RANGES = ("PREVIOUS_DAY", "LAST_30_DAYS", "LAST_90_DAYS", "LAST_7_DAYS", "PREVIOUS_MONTH", "PREVIOUS_WEEK")
POSSIBLE_REQUEST_TYPES = [
    "existing_query",
    "custom_query",
    "existing_query_report",
    "custom_query_report",
    "lineitems_objects",
    "list_reports",
]


class GoogleDBMReaderConfig(BaseModel):
    access_toekn: str = None
    refresh_token: str
    client_id: str
    client_secret: str
    metric: List[str] = []
    dimension: List[str] = []
    request_type: Literal[tuple(POSSIBLE_REQUEST_TYPES)]
    query_id: str = None
    query_title: str = None
    query_frequency: str = "ONE_TIME"
    query_param_type: str = "TYPE_TRUEVIEW"
    start_date: datetime = None
    end_date: datetime = None
    add_date_to_report: bool = False
    filter: List[Tuple[str, str]] = []
    file_type: List[str] = []
    date_format: str = "%Y-%m-%d"
    day_range: Literal[DAY_RANGES] = None

    @validator("start_date", "end_date", pre=True)
    def date_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Datetime format must follow 'YYYY-MM-DD'")
        return v
