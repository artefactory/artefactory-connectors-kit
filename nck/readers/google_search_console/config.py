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

from pydantic import BaseModel

from nck.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS

DATEFORMAT = "%Y-%m-%d"
GOOGLE_TOKEN_URI = "https://accounts.google.com/o/oauth2/token"


class GoogleSearchConsoleReaderConfig(BaseModel):
    client_id: str
    client_secret: str
    access_token: str = ""
    refresh_token: str
    dimensions: List[str]
    site_url: str
    start_date: datetime = None
    end_date: datetime = None
    date_column: bool = False
    row_limit: int = 25000
    date_range: Literal[tuple(DEFAULT_DATE_RANGE_FUNCTIONS.keys())] = None
