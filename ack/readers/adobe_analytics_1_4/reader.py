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

# Credit goes to Mr Martin Winkel for the base code provided :
# github : https://github.com/SaturnFromTitan/adobe_analytics

import datetime
import json
from itertools import chain
from time import sleep

import requests
from click import ClickException
from ack.clients.adobe_analytics.client import AdobeAnalyticsClient
from ack.config import logger
from ack.readers.adobe_analytics_1_4.config import ADOBE_API_ENDPOINT, MAX_WAIT_REPORT_DELAY
from ack.readers.adobe_analytics_1_4.helper import parse
from ack.readers.reader import Reader
from ack.streams.json_stream import JSONStream
from ack.utils.date_handler import check_date_range_definition_conformity
from ack.utils.exceptions import ReportDescriptionError, ReportNotReadyError
from ack.utils.retry import retry


class AdobeAnalytics14Reader(Reader):
    def __init__(
        self, client_id, client_secret, tech_account_id, org_id, private_key, global_company_id, **kwargs,
    ):
        self.adobe_client = AdobeAnalyticsClient(client_id, client_secret, tech_account_id, org_id, private_key)
        self.global_company_id = global_company_id
        self.kwargs = kwargs

        check_date_range_definition_conformity(
            self.kwargs.get("start_date"), self.kwargs.get("end_date"), self.kwargs.get("day_range")
        )

    def request(self, api, method, data=None):
        """
        Makes "raw" HTTP requests to Reporting API 1.4 (used within the query_report and get_report methods)
        API workflow: https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/reporting-api/get_started.md
        """
        api_method = f"{api}.{method}"
        data = data or dict()
        logger.info(f"{api}.{method} {data}")
        response = requests.post(
            ADOBE_API_ENDPOINT,
            params={"method": api_method},
            data=json.dumps(data),
            headers=self.adobe_client.build_request_headers(self.global_company_id),
        )
        json_response = response.json()
        logger.debug(f"Response: {json_response}")
        return json_response

    def build_report_description(self):
        """
        Builds the reportDescription to be passed to the Report.Queue method as an input parameter.
        Source is set at "warehouse" to get Data Wharehouse reports, and access multiple report pages.
        Doc: https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/reporting-api/data_types/r_reportDescription.md
        """
        report_description = {
            "reportDescription": {
                "source": "warehouse",
                "reportSuiteID": self.kwargs.get("report_suite_id"),
                "elements": [{"id": el} for el in self.kwargs.get("report_element_id", [])],
                "metrics": [{"id": mt} for mt in self.kwargs.get("report_metric_id", [])],
            }
        }
        self.set_date_gran_report_desc(report_description)
        self.set_date_range_report_desc(report_description)
        logger.debug(f"report_description content {report_description}")
        return report_description

    def get_days_delta(self):
        days_range = self.kwargs.get("day_range")
        delta_mapping = {
            "PREVIOUS_DAY": 1,
            "LAST_7_DAYS": 7,
            "LAST_30_DAYS": 30,
            "LAST_90_DAYS": 90,
        }
        try:
            days_delta = delta_mapping[days_range]
        except KeyError:
            raise ClickException(f"{days_range} is not handled by the reader")
        return days_delta

    def set_date_range_report_desc(self, report_description):
        """
        Adds the dateFrom and dateTo parameters to a reportDescription.
        """
        if self.kwargs.get("date_range") != ():
            start_date = self.kwargs.get("start_date")
            end_date = self.kwargs.get("end_date", datetime.datetime.now())
        else:
            end_date = datetime.datetime.now().date()
            start_date = end_date - datetime.timedelta(days=self.get_days_delta())
        report_description["reportDescription"]["dateFrom"] = start_date.strftime("%Y-%m-%d")
        report_description["reportDescription"]["dateTo"] = end_date.strftime("%Y-%m-%d")

    def set_date_gran_report_desc(self, report_description):
        """
        Adds the dateGranularity parameter to a reportDescription.
        """
        if self.kwargs.get("date_granularity", None) is not None:
            report_description["reportDescription"]["dateGranularity"] = self.kwargs.get("date_granularity")

    @retry
    def query_report(self):
        """
        REQUEST STEP #1
        - Method: Report.Queue
        - Input: reportDescription
        - Output: reportID, to be passed to the Report.Get method
        - Doc: https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/reporting-api/methods/r_Queue.md
        """
        query_report = self.request(api="Report", method="Queue", data=self.build_report_description())
        return query_report

    @retry
    def get_report(self, report_id, page_number=1):
        """
        REQUEST STEP #2
        - Method: Report.Get
        - Input: reportID, page
        - Output: reportResponse containing the requested report data
        - Doc: https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/reporting-api/methods/r_Get.md
        """

        def request_f():
            return self.request(api="Report", method="Get", data={"reportID": report_id, "page": page_number},)

        response = request_f()
        idx = 1
        while response.get("error") == "report_not_ready":
            logger.info(f"waiting {idx} s for report to be ready")
            sleep(idx + 1)
            if idx + 1 > MAX_WAIT_REPORT_DELAY:
                raise ReportNotReadyError("waited too long for report to be ready")
            idx = idx * 2
            response = request_f()
        return response

    def download_report(self, rep_id):
        """
        Parses reportResponses and iterates over report pages.
        """
        raw_response = self.get_report(rep_id, page_number=1)
        if raw_response.get("error") != "no_warehouse_data":
            all_responses = [parse(raw_response)]
            if "totalPages" in raw_response["report"]:
                all_responses = all_responses + [
                    parse(self.get_report(rep_id, page_number=np)) for np in range(2, raw_response["report"]["totalPages"] + 1)
                ]
            return chain(*all_responses)

    def read(self):
        if self.kwargs.get("list_report_suite", False):
            r = self.request("Company", "GetReportSuites")
            data = r["report_suites"]
            idf = "list_rps"
        else:
            query_rep = self.query_report()
            if query_rep.get("error"):
                raise ReportDescriptionError(query_rep)
            else:
                rep_id = query_rep["reportID"]
                data = self.download_report(rep_id)
                idf = "report_" + str(rep_id)

        def result_generator():
            if data:
                yield from data

        yield JSONStream("results_" + idf, result_generator())
