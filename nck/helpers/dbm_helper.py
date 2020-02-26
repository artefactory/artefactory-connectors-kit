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
POSSIBLE_REQUEST_TYPES = [
    "existing_query",
    "custom_query",
    "existing_query_report",
    "custom_query_report",
    "lineitems_objects",
    "sdf_objects",
    "list_reports",
]

POSSIBLE_SDF_FILE_TYPES = [
    "INVENTORY_SOURCE",
    "AD",
    "AD_GROUP",
    "CAMPAIGN",
    "INSERTION_ORDER",
    "LINE_ITEM",
]

FILE_TYPES_DICT = {
    "AD": "ads",
    "AD_GROUP": "adGroups",
    "CAMPAIGN": "campaigns",
    "LINE_ITEM": "lineItems",
    "INSERTION_ORDER": "insertionOrders",
}
