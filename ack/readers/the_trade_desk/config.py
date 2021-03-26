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

from ack.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS

API_HOST = "https://api.thetradedesk.com/v3"

API_ENDPOINTS = {
    "get_report_template_id": ("POST", "myreports/reporttemplateheader/query"),
    "create_report_schedule": ("POST", "myreports/reportschedule"),
    "get_report_execution_details": ("POST", "myreports/reportexecution/query/advertisers",),
    "delete_report_schedule": ("DELETE", "/myreports/reportschedule"),
}

DEFAULT_REPORT_SCHEDULE_ARGS = {
    "ReportFileFormat": "CSV",
    "ReportDateRange": "Custom",
    "TimeZone": "UTC",
    "ReportDateFormat": "Sortable",
    "ReportNumericFormat": "US",
    "IncludeHeaders": True,
    "ReportFrequency": "Once",
}

DEFAULT_PAGING_ARGS = {
    "PageStartIndex": 0,
    "PageSize": 10,
}

API_DATEFORMAT = "%Y-%m-%dT%H:%M:%S"
BQ_DATEFORMAT = "%Y-%m-%d"


class TheTradeDeskReaderConfig(BaseModel):
    login: str
    password: str
    advertiser_id: List[str]
    report_template_name: str
    report_schedule_name: str
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
