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

from datetime import timedelta

import requests
from click import ClickException
from nck.config import logger
from nck.readers.reader import Reader
from nck.readers.the_trade_desk.config import API_ENDPOINTS, API_HOST, DEFAULT_PAGING_ARGS, DEFAULT_REPORT_SCHEDULE_ARGS
from nck.readers.the_trade_desk.helper import format_date
from nck.streams.json_stream import JSONStream
from nck.utils.exceptions import ReportScheduleNotReadyError, ReportTemplateNotFoundError
from nck.utils.text import get_report_generator_from_flat_file
from tenacity import retry, stop_after_delay, wait_exponential


class TheTradeDeskReader(Reader):
    def __init__(self, login, password, advertiser_id, report_template_name, report_schedule_name, start_date, end_date):
        self.login = login
        self.password = password
        self._build_headers()
        self.advertiser_ids = list(advertiser_id)
        self.report_template_name = report_template_name
        self.report_schedule_name = report_schedule_name
        self.start_date = start_date
        # Report end date is exclusive: to become inclusive, it should be incremented by 1 day
        self.end_date = end_date + timedelta(days=1)

        self._validate_dates()

    def _validate_dates(self):
        if self.end_date - timedelta(days=1) < self.start_date:
            raise ClickException("Report end date should be equal or ulterior to report start date.")

    def _get_access_token(self):
        url = f"{API_HOST}/authentication"
        headers = {"Content-Type": "application/json"}
        payload = {
            "Login": self.login,
            "Password": self.password,
            "TokenExpirationInMinutes": 1440,
        }
        response = requests.post(url=url, headers=headers, json=payload)
        if response.ok:
            return response.json()["Token"]
        else:
            response.raise_for_status()

    def _build_headers(self):
        self.headers = {"Content-Type": "application/json", "TTD-Auth": self._get_access_token()}

    def _make_api_call(self, method, endpoint, payload={}):
        url = f"{API_HOST}/{endpoint}"
        response = requests.request(method=method, url=url, headers=self.headers, json=payload)
        if response.ok:
            if response.content:
                return response.json()
        else:
            response.raise_for_status()

    def _get_report_template_id(self):
        logger.info(f"Collecting ReportTemplateId of '{self.report_template_name}'")
        method, endpoint = API_ENDPOINTS["get_report_template_id"]
        payload = {"NameContains": self.report_template_name, **DEFAULT_PAGING_ARGS}
        json_response = self._make_api_call(method, endpoint, payload)
        if json_response["ResultCount"] == 0:
            raise ReportTemplateNotFoundError(f"No existing ReportTemplate match '{self.report_template_name}'")
        if json_response["ResultCount"] > 1:
            raise ReportTemplateNotFoundError(
                f"""'{self.report_template_name}' match more than one ReportTemplate.
                Please specify the exact name of the ReportTemplate you wish to retrieve."""
            )
        else:
            self.report_template_id = json_response["Result"][0]["ReportTemplateId"]
            logger.info(f"Retrieved ReportTemplateId: {self.report_template_id}")

    def _create_report_schedule(self):
        method, endpoint = API_ENDPOINTS["create_report_schedule"]
        payload = {
            "ReportScheduleName": self.report_schedule_name,
            "ReportTemplateId": self.report_template_id,
            "AdvertiserFilters": self.advertiser_ids,
            "ReportStartDateInclusive": self.start_date.isoformat(),
            "ReportEndDateExclusive": self.end_date.isoformat(),
            **DEFAULT_REPORT_SCHEDULE_ARGS,
        }
        logger.info(f"Creating ReportSchedule: {payload}")
        json_response = self._make_api_call(method, endpoint, payload)
        self.report_schedule_id = json_response["ReportScheduleId"]

    @retry(
        wait=wait_exponential(multiplier=1, min=60, max=3600),
        stop=stop_after_delay(36000),
    )
    def _wait_for_download_url(self):
        report_execution_details = self._get_report_execution_details()
        if report_execution_details["ReportExecutionState"] == "Pending":
            raise ReportScheduleNotReadyError(f"ReportSchedule '{self.report_schedule_id}' is still running.")
        else:
            # As the ReportSchedule that we just created runs only once,
            # the API response will include only one ReportDelivery (so we can get index "[0]")
            self.download_url = report_execution_details["ReportDeliveries"][0]["DownloadURL"]
            logger.info(f"ReportScheduleId '{self.report_schedule_id}' is ready. DownloadURL: {self.download_url}")

    def _get_report_execution_details(self):
        method, endpoint = API_ENDPOINTS["get_report_execution_details"]
        payload = {
            "AdvertiserIds": self.advertiser_ids,
            "ReportScheduleIds": [self.report_schedule_id],
            **DEFAULT_PAGING_ARGS,
        }
        json_response = self._make_api_call(method, endpoint, payload)
        # As the ReportScheduleId that we provided as a payload is globally unique,
        # the API response will include only one Result (so we can get index "[0]")
        report_execution_details = json_response["Result"][0]
        return report_execution_details

    def _download_report(self):
        report = requests.get(url=self.download_url, headers=self.headers, stream=True)
        return get_report_generator_from_flat_file(report.iter_lines())

    def _delete_report_schedule(self):
        logger.info(f"Deleting ReportScheduleId '{self.report_schedule_id}'")
        method, endpoint = API_ENDPOINTS["delete_report_schedule"]
        self._make_api_call(method, f"{endpoint}/{self.report_schedule_id}")

    def read(self):
        self._get_report_template_id()
        self._create_report_schedule()
        self._wait_for_download_url()
        data = self._download_report()

        def result_generator():
            for record in data:
                yield {k: format_date(v) if k == "Date" else v for k, v in record.items()}

        yield JSONStream("results_" + "_".join(self.advertiser_ids), result_generator())

        self._delete_report_schedule()
