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

DATEFORMAT = "%Y-%m-%dT%H:%M:%S"
API_WINDOW_DURATION = 6
API_REQUESTS_OVER_WINDOW_LIMIT = 12


class AdobeAnalytics20ReaderConfig(BaseModel):
    client_id: str
    client_secret: str
    tech_account_id: str
    org_id: str
    private_key: str
    global_company_id: str
    report_suite_id: str
    dimension: List[str]
    metric: List[str]
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

    @validator("private_key")
    def format_key_if_needed(cls, v):
        """
        From the old Click behavior. In case if needed.
        In some cases, newlines are escaped when passed as a click.option().
        This callback corrects this unexpected behaviour.
        """
        return v.replace("\\n", "\n")
