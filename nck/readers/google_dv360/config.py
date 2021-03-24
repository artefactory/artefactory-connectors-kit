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
from typing import Literal, List

from pydantic import BaseModel

FILE_NAMES = {
    "FILE_TYPE_INSERTION_ORDER": "InsertionOrders",
    "FILE_TYPE_CAMPAIGN": "Campaigns",
    "FILE_TYPE_MEDIA_PRODUCT": "MediaProducts",
    "FILE_TYPE_LINE_ITEM": "LineItems",
    "FILE_TYPE_AD_GROUP": "AdGroups",
    "FILE_TYPE_AD": "AdGroupAds",
}

FILE_TYPES = FILE_NAMES.keys()

FILTER_TYPES = [
    "FILTER_TYPE_UNSPECIFIED",
    "FILTER_TYPE_NONE",
    "FILTER_TYPE_ADVERTISER_ID",
    "FILTER_TYPE_CAMPAIGN_ID",
    "FILTER_TYPE_MEDIA_PRODUCT_ID",
    "FILTER_TYPE_INSERTION_ORDER_ID",
    "FILTER_TYPE_LINE_ITEM_ID",
]

REQUEST_TYPES = ["sdf_request", "creative_request"]


class GoogleDV360ReaderConfig(BaseModel):
    access_token: str = None
    refresh_token: str
    client_id: str
    client_secret: str
    advertiser_id: str
    request_type: Literal[tuple(REQUEST_TYPES)]
    file_type: List[Literal[tuple(FILE_TYPES)]] = []
    filter_type: Literal[tuple(FILTER_TYPES)] = None
