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
from typing import List, Literal

from pydantic import BaseModel

YANDEX_DIRECT_API_BASE_URL = "https://api.direct.yandex.com/json/v5/"

CAMPAIGN_FIELDS = [
    "BlockedIps",
    "ExcludedSites",
    "Currency",
    "DailyBudget",
    "Notification",
    "EndDate",
    "Funds",
    "ClientInfo",
    "Id",
    "Name",
    "NegativeKeywords",
    "RepresentedBy",
    "StartDate",
    "Statistics",
    "State",
    "Status",
    "StatusPayment",
    "StatusClarification",
    "SourceId",
    "TimeTargeting",
    "TimeZone",
    "Type",
]

CAMPAIGN_STATES = ["ARCHIVED", "CONVERTED", "ENDED", "OFF", "ON", "SUSPENDED"]

CAMPAIGN_STATUSES = ["ACCEPTED", "DRAFT", "MODERATION", "REJECTED"]

CAMPAIGN_PAYMENT_STATUSES = ["ALLOWED", "DISALLOWED"]


class YandexCampaignReaderConfig(BaseModel):
    token: str
    campaign_ids: List[str] = []
    campaign_states: List[Literal[tuple(CAMPAIGN_STATES)]] = []
    campaign_statuses: List[Literal[tuple(CAMPAIGN_STATUSES)]] = []
    campaign_payment_statuses: List[Literal[tuple(CAMPAIGN_PAYMENT_STATUSES)]] = []
    fields: List[Literal[tuple(CAMPAIGN_FIELDS)]] = []
