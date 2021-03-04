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

ENCODING = "utf-8"

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
