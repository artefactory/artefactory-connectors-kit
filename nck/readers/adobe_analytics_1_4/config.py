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

ADOBE_API_ENDPOINT = "https://api.omniture.com/admin/1.4/rest/"
LIMIT_NVIEWS_PER_REQ = 5
MAX_WAIT_REPORT_DELAY = 4096
DAY_RANGE = ("PREVIOUS_DAY", "LAST_30_DAYS", "LAST_7_DAYS", "LAST_90_DAYS")


class AdobeAnalytics14ReaderConfig(BaseModel):
    client_id: str
    client_secret: str
    tech_account_id: str
    ord_id: str
    private_key: str
    global_company_id: str
    list_report_suite: bool = False
    report_suite_id: str = None
    report_element_id: List[str] = []
    report_metric_id: List[str] = []
    date_granularity: str = None
    day_range: Literal[DAY_RANGE] = None
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

    @validator("private_key")
    def format_key_if_needed(cls, v):
        """
        From the old Click behavior. In case if needed.
        In some cases, newlines are escaped when passed as a click.option().
        This callback corrects this unexpected behaviour.
        """
        return v.replace("\\n", "\n")
