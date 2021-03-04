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

from nck.config import logger
import httplib2
import requests

from tenacity import retry, wait_exponential, stop_after_delay
from oauth2client import client, GOOGLE_TOKEN_URI
from googleapiclient import discovery

DOWNLOAD_FORMAT = "CSV"


class SA360Client:
    API_NAME = "doubleclicksearch"
    API_VERSION = "v2"

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

    def get_all_advertisers_of_agency(self, agency_id):
        body = {
            "reportScope": {"agencyId": agency_id},
            "reportType": "advertiser",
            "columns": [{"columnName": "advertiserId"}],
            "statisticsCurrency": "usd",
        }
        report = self._service.reports().generate(body=body).execute()
        advertiser_ids = [row["advertiserId"] for row in report["rows"]]
        return advertiser_ids

    @staticmethod
    def generate_report_body(agency_id, advertiser_id, report_type, columns, start_date, end_date, saved_columns):
        all_columns = SA360Client.generate_columns(columns, saved_columns)
        body = {
            "reportScope": {"agencyId": agency_id, "advertiserId": advertiser_id},
            "reportType": report_type,
            "columns": all_columns,
            "timeRange": SA360Client.get_date_range(start_date, end_date),
            "downloadFormat": "csv",
            "maxRowsPerFile": 4000000,
            "statisticsCurrency": "usd",
        }
        logger.info("Report Body Generated")
        return body

    def request_report_id(self, body):
        report = self._service.reports().request(body=body).execute()
        logger.info("Report requested!")
        return report["id"]

    @retry(wait=wait_exponential(multiplier=60, min=60, max=600), stop=stop_after_delay(3600))
    def assert_report_file_ready(self, report_id):
        """Poll the API with the reportId until the report is ready, up to 100 times.

        Args:
          report_id: The ID SA360 has assigned to a report.
        """
        request = self._service.reports().get(reportId=report_id)
        report_data = request.execute()
        if report_data["isReportReady"]:
            logger.info("The report is ready.")

            # For large reports, SA360 automatically fragments the report into multiple
            # files. The 'files' property in the JSON object that SA360 returns contains
            # the list of URLs for file fragment. To download a report, SA360 needs to
            # know the report ID and the index of a file fragment.
            return report_data
        else:
            logger.info("Report is not ready. Retrying...")
            raise FileNotFoundError

    def download_report_files(self, json_data, report_id):
        for fragment in range(len(json_data["files"])):
            logger.info(f"Downloading fragment {str(fragment)} for report {report_id}")
            yield self.download_fragment(report_id, str(fragment))

    def download_fragment(self, report_id, fragment):
        """Generate and convert to df a report fragment.

        Args:
          report_id: The ID SA360 has assigned to a report.
          fragment: The 0-based index of the file fragment from the files array.
        """
        request = self._service.reports().getFile(reportId=report_id, reportFragment=fragment)
        headers = request.headers
        headers.update({"Authorization": self.auth})
        r = requests.get(request.uri, stream=True, headers=headers)

        yield from r.iter_lines()

    def direct_report_download(self, report_id, file_id):
        # Retrieve the file metadata.
        report_file = self._service.files().get(reportId=report_id, fileId=file_id).execute()

        if report_file["status"] == "REPORT_AVAILABLE":
            # Create a get request.
            request = self._service.files().get_media(reportId=report_id, fileId=file_id)
            headers = request.headers
            r = requests.get(request.uri, stream=True, headers=headers)

            yield from r.iter_lines()

    @staticmethod
    def generate_columns(columns, saved_columns):
        standard = [{"columnName": column} for column in columns]
        saved = [{"savedColumnName": column} for column in saved_columns]

        return standard + saved

    @staticmethod
    def get_date_range(start_date, end_date):
        start = start_date.strftime("%Y-%m-%d")
        end = end_date.strftime("%Y-%m-%d")
        logger.warning(f"Custom date range selected: {start} --> {end}")
        return {"startDate": start, "endDate": end}
