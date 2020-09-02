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

import requests
from datetime import datetime
import logging

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


class ReportTemplateNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)
        logging.error(message)


class ReportScheduleNotReadyError(Exception):
    def __init__(self, message):
        super().__init__(message)
        logging.error(message)


def build_headers(login, password):
    access_token = get_access_token(login, password)
    return {"Content-Type": "application/json", "TTD-Auth": access_token}


def get_access_token(login, password):
    url = f"{API_HOST}/authentication"
    headers = {"Content-Type": "application/json"}
    payload = {
        "Login": login,
        "Password": password,
        "TokenExpirationInMinutes": 1440,
    }
    response = requests.post(url=url, headers=headers, json=payload)
    if response.ok:
        return response.json()["Token"]
    else:
        response.raise_for_status()


def format_date(date_string):
    """
    Input: "2020-01-01T00:00:00"
    Output: "2020-01-01"
    """
    return datetime.strptime(date_string, API_DATEFORMAT).strftime(BQ_DATEFORMAT)
