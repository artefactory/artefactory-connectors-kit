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

API_HOST = "https://api.thetradedesk.com/v3"

API_ENDPOINTS = {
    "get_report_template_id": ("POST", "myreports/reporttemplateheader/query"),
    "create_report_schedule": ("POST", "myreports/reportschedule"),
    "get_report_execution_details": (
        "POST",
        "myreports/reportexecution/query/advertisers",
    ),
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
