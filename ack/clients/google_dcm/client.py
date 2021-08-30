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

from ack.config import logger
from ack.utils.exceptions import FilterNotFoundError
import httplib2
import requests

from tenacity import retry, wait_exponential, stop_after_delay
from oauth2client import client, GOOGLE_TOKEN_URI
from googleapiclient import discovery

DOWNLOAD_FORMAT = "CSV"


class GoogleDCMClient:
    API_NAME = "dfareporting"
    API_VERSION = "v3.5"

    def __init__(self, access_token, client_id, client_secret, refresh_token):
        self._credentials = client.GoogleCredentials(
            access_token=access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            token_expiry=None,
            token_uri=GOOGLE_TOKEN_URI,
            user_agent=None,
        )
        http = self._credentials.authorize(httplib2.Http())
        self._credentials.refresh(http)
        self.auth = f"{self._credentials.token_response['token_type']} {self._credentials.token_response['access_token']}"
        self._service = discovery.build(self.API_NAME, self.API_VERSION, http=http, cache_discovery=False)

    @staticmethod
    def build_report_skeleton(report_name, report_type):
        report = {
            # Set the required fields "name" and "type".
            "name": report_name,
            "type": report_type,
            "format": DOWNLOAD_FORMAT,
        }
        return report

    def add_report_criteria(self, report, start_date, end_date, metrics, dimensions):
        criteria = {
            "dateRange": self.get_date_range(start_date, end_date),
            "dimensions": [{"name": dim} for dim in dimensions],
            "metricNames": metrics,
        }
        if report["type"] == "REACH":
            report["reachCriteria"] = criteria
        elif report["type"] == "PATH_TO_CONVERSION":
            report["pathToConversionCriteria"] = criteria
        elif report["type"] == "FLOODLIGHT":
            report["floodlightCriteria"] = criteria
        elif report["type"] == "CROSS_DIMENSION_REACH":
            report["crossDimensionReachCriteria"] = criteria
        else:  # Standard Report Criteria
            report["criteria"] = criteria

    def add_dimension_filters(self, report, profile_id, filters):
        if report["type"] == "REACH":
            criteria = "reachCriteria"
        elif report["type"] == "PATH_TO_CONVERSION":
            criteria = "pathToConversionCriteria"
        elif report["type"] == "FLOODLIGHT":
            criteria = "floodlightCriteria"
        elif report["type"] == "CROSS_DIMENSION_REACH":
            criteria = "crossDimensionReachCriteria"
        else:  # Standard Report Criteria
            criteria = "criteria"

        for dimension_name, dimension_value in filters:
            request = {
                "dimensionName": dimension_name,
                "startDate": report[criteria]["dateRange"]["startDate"],
                "endDate": report[criteria]["dateRange"]["endDate"],
            }
            values = self._service.dimensionValues().query(profileId=profile_id, body=request).execute()
            current_values = values

            while current_values["items"]:
                nextPageToken = current_values["nextPageToken"]
                current_values = (
                    self._service.dimensionValues()
                    .query(profileId=profile_id, body=request, pageToken=nextPageToken)
                    .execute()
                )
                values["items"] += current_values["items"]

            report[criteria]["dimensionFilters"] = report[criteria].get("dimensionFilters", [])
            if values["items"]:
                # Add value as a filter to the report criteria.
                filter_value = self.get_filter_value(dimension_value, values)
                if filter_value:
                    report[criteria]["dimensionFilters"].append(filter_value)
                else:
                    raise FilterNotFoundError(f"Filter not found: {dimension_name} - {dimension_value}")

    def run_report(self, report, profile_id):
        inserted_report = self._service.reports().insert(profileId=profile_id, body=report).execute()
        report_id = inserted_report["id"]
        file = self._service.reports().run(profileId=profile_id, reportId=report_id).execute()
        file_id = file["id"]
        return report_id, file_id

    @retry(wait=wait_exponential(multiplier=60, min=60, max=240), stop=stop_after_delay(36000))
    def assert_report_file_ready(self, report_id, file_id):
        """Poke the report file status"""
        report_file = self._service.files().get(reportId=report_id, fileId=file_id).execute()

        status = report_file["status"]
        if status == "REPORT_AVAILABLE":
            logger.info(f"File status is {status}, ready to download.")
            pass
        elif status != "PROCESSING":
            raise FileNotFoundError(f"File status is {status}, processing failed.")
        else:
            raise FileNotFoundError("File status is PROCESSING")

    def direct_report_download(self, report_id, file_id):
        # Retrieve the file metadata.
        report_file = self._service.files().get(reportId=report_id, fileId=file_id).execute()

        if report_file["status"] == "REPORT_AVAILABLE":
            # Create a get request.
            self.auth = f"{self._credentials.token_response['token_type']} {self._credentials.token_response['access_token']}"
            request = self._service.files().get_media(reportId=report_id, fileId=file_id)
            headers = request.headers
            headers.update({"Authorization": self.auth})
            r = requests.get(request.uri, stream=True, headers=headers)

            yield from r.iter_lines()

    @staticmethod
    def get_date_range(start_date=None, end_date=None):
        if start_date and end_date:
            start = start_date.strftime("%Y-%m-%d")
            end = end_date.strftime("%Y-%m-%d")
            logger.warning(f"Custom date range selected: {start} --> {end}")
            return {"startDate": start, "endDate": end}
        else:
            raise SyntaxError("Please provide start date and end date in your request")

    @staticmethod
    def get_filter_value(dimension_value, values):
        return next((val for val in values["items"] if val["value"] == dimension_value), {})
