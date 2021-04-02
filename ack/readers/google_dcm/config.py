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

from ack.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS

ENCODING = "utf-8"
PREFIX = "^dfa:"

CRITERIA_MAPPING = {
    "STANDARD": "criteria",
    "REACH": "reachCriteria",
    "PATH_TO_CONVERSION": "pathToConversionCriteria",
    "FLOODLIGHT": "floodlightCriteria",
    "CROSS_DIMENSION_REACH": "crossDimensionReachCriteria",
}

REPORT_TYPES = list(CRITERIA_MAPPING.keys())

DATE_RANGES = [
    "LAST_14_DAYS",
    "LAST_24_MONTHS",
    "LAST_30_DAYS",
    "LAST_365_DAYS",
    "LAST_60_DAYS",
    "LAST_7_DAYS",
    "LAST_90_DAYS",
    "MONTH_TO_DATE",
    "PREVIOUS_MONTH",
    "PREVIOUS_QUARTER",
    "PREVIOUS_WEEK",
    "PREVIOUS_YEAR",
    "QUARTER_TO_DATE",
    "TODAY",
    "WEEK_TO_DATE",
    "YEAR_TO_DATE",
    "YESTERDAY",
]


class GoogleDCMReaderConfig(BaseModel):
    access_token: str = None
    client_id: str
    client_secret: str
    refresh_token: str
    profile_ids: List[str]
    report_name: str = "DCM Report"
    report_type: Literal[tuple(REPORT_TYPES)] = REPORT_TYPES[0]
    metrics: List[str] = []
    dimensions: List[str] = []
    start_date: datetime = None
    end_date: datetime = None
    filters: List[Tuple[str, str]] = []
    date_range: Literal[tuple(DEFAULT_DATE_RANGE_FUNCTIONS.keys())] = None

    @validator("start_date", "end_date", pre=True)
    def date_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Datetime format must follow 'YYYY-MM-DD'")
        return v
