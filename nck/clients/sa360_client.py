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
import logging
import httplib2
import requests

from tenacity import retry, wait_exponential, stop_after_delay
from oauth2client import client, GOOGLE_TOKEN_URI
from googleapiclient import discovery


logger = logging.getLogger("SA360_client")

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
        self.auth = (
            f"{self._credentials.token_response['token_type']} {self._credentials.token_response['access_token']}"
        )
        self._service = discovery.build(self.API_NAME, self.API_VERSION, http=http, cache_discovery=False)

    @staticmethod
    def generate_report_body(
        agency_id, advertiser_id, report_type, columns, start_date, end_date, custom_metrics, custom_dimensions
    ):
        all_columns = SA360Client.generate_columns(columns, custom_metrics, custom_dimensions)
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

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_delay(3600))
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
            logger.info("Report is not ready.")
            raise FileNotFoundError

    def download_report_files(self, json_data, report_id):
        for fragment in range(len(json_data["files"])):
            logger.info(f"Downloading fragment {str(fragment)} for report {report_id}")
            yield self.download_fragment(report_id, str(fragment))

    def download_fragment(self, report_id, fragment):
        """Generate and convert to df a report fragment.

                Args:
                  report_id: The ID SA360 has assigned to a report.
                  report_fragment: The 0-based index of the file fragment from the files array.
                  currency_code: the currency code of the report
                """
        # csv_fragment_report = (self._service.reports().getFile(reportId=report_id, reportFragment=fragment).execute())
        # print(csv_fragment_report)
        # print(io.BytesIO(csv_fragment_report))
        request = self._service.reports().getFile(reportId=report_id, reportFragment=fragment)
        headers = request.headers
        headers.update({"Authorization": self.auth})
        r = requests.get(request.uri, stream=True, headers=headers)

        yield from r.iter_lines()

        # i = 0
        # index = 0
        # impr_keyword = 0
        # for row in r.iter_lines():
        #     decoded_row = row.decode("utf-8")
        #     if "impr" in decoded_row:
        #         decoded_row = decoded_row.split(",")
        #         index = decoded_row.index("impr")
        #         continue
        #
        #     if "samsung note 10+ 6.8" in decoded_row:
        #         r = decoded_row.split(",")
        #         impr_keyword += int(r[index])
        #     print(decoded_row)
        #     decoded_row = decoded_row.split(",")
        #     i += int(decoded_row[index])
        # print("IMPRESSIONS", i, impr_keyword)

        # yield from r.iter_lines()

        # df = pd.DataFrame.from_csv(io.BytesIO(csv_fragment_report))
        # df["currency_code"] = currency_code
        # from tabulate import tabulate
        # print(tabulate(df, headers='keys', tablefmt='psql'))
        # return df

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
    def generate_columns(columns, custom_dimensions, custom_metrics):
        standard = [{"columnName": column} for column in columns]
        dimensions = [{"columnDimensionName": column, "platformSource": "floodlight"} for column in custom_dimensions]
        metrics = [{"columnMetricName": column, "platformSource": "floodlight"} for column in custom_metrics]

        return standard + dimensions + metrics

    @staticmethod
    def get_date_range(start_date, end_date):
        start = start_date.strftime("%Y-%m-%d")
        end = end_date.strftime("%Y-%m-%d")
        logger.warning(f"Custom date range selected: {start} --> {end}")
        return {"startDate": start, "endDate": end}
