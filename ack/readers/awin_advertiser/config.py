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

DATEFORMAT = "%Y-%m-%d"

AWIN_API_ENDPOINT = "https://api.awin.com/advertisers/"
LIMIT_NVIEWS_PER_REQ = 5
MAX_WAIT_REPORT_DELAY = 4096

# https://wiki.awin.com/index.php/Advertiser_Service_API
REPORT_TYPES = [
    "publisher",
    "creative",
    "campaign"
]


class AwinAdvertiserReaderConfig(BaseModel):
    auth_token: str
    advertiser_id: str
    report_type: Literal[tuple(REPORT_TYPES)]
    region: str
    timezone: str
    start_date: datetime = None
    end_date: datetime = None

    @validator("start_date", "end_date", pre=True)
    def date_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, DATEFORMAT)
            except ValueError:
                raise ValueError("Datetime format must follow 'YYYY-MM-DD'")
        return v
