import logging
import httplib2
import requests

from click import ClickException
from tenacity import retry, wait_exponential, stop_after_delay

from oauth2client import client, GOOGLE_TOKEN_URI
from googleapiclient import discovery

logger = logging.getLogger("CM_client")


class DCMClient:
    API_NAME = "dfareporting"
    API_VERSION = "v3.3"

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
            self._credentials.token_response["token_type"] + " " + self._credentials.token_response["access_token"]
        )
        self._service = discovery.build(self.API_NAME, self.API_VERSION, http=http, cache_discovery=False)
        self.download_format = "CSV"

    def build_report_skeleton(self, report_name, report_type):
        report = {
            # Set the required fields "name" and "type".
            "name": report_name,
            "type": report_type,
            "format": self.download_format,
        }
        return report

    @staticmethod
    def get_date_range(start_date=None, end_date=None):
        if start_date and end_date:
            start = start_date.strftime("%Y-%m-%d")
            end = end_date.strftime("%Y-%m-%d")
            logger.warning("Custom date range selected: " + start + " --> " + end)
            return {"startDate": start, "endDate": end}
        else:
            raise ClickException("Please provide start date and end date in your request")

    def add_report_criteria(self, report, start_date, end_date, metrics, dimensions):
        criteria = {
            "dateRange": self.get_date_range(start_date, end_date),
            "dimensions": [{"name": dim} for dim in dimensions],
            "metricNames": metrics,
        }
        report["criteria"] = criteria

    def add_dimension_filters(self, report, profile_id, filters):
        for dimension_name, dimension_value in filters:
            request = {
                "dimensionName": dimension_name,
                "endDate": report["criteria"]["dateRange"]["endDate"],
                "startDate": report["criteria"]["dateRange"]["startDate"],
            }
            values = self._service.dimensionValues().query(profileId=profile_id, body=request).execute()

            report["criteria"]["dimensionFilters"] = report["criteria"].get("dimensionFilters", [])
            if values["items"]:
                # Add value as a filter to the report criteria.
                filter_value = next((val for val in values["items"] if val["value"] == dimension_value), {})
                if filter_value:
                    report["criteria"]["dimensionFilters"].append(filter_value)

    def run_report(self, report, profile_id):
        inserted_report = self._service.reports().insert(profileId=profile_id, body=report).execute()
        report_id = inserted_report["id"]
        file = self._service.reports().run(profileId=profile_id, reportId=report_id).execute()
        file_id = file["id"]
        return report_id, file_id

    # @retry(wait=wait_exponential(multiplier=60, min=60, max=240), stop=stop_after_delay(3600))
    @retry(wait=wait_exponential(multiplier=1, min=1, max=4), stop=stop_after_delay(3600))
    def is_report_file_ready(self, report_id, file_id):
        """Poke the report file status"""
        report_file = self._service.files().get(reportId=report_id, fileId=file_id).execute()

        status = report_file["status"]
        if status == "REPORT_AVAILABLE":
            logger.info("File status is %s, ready to download." % status)
            return True
        elif status != "PROCESSING":
            raise ClickException("File status is %s, processing failed." % status)
        else:
            raise ClickException("File status is PROCESSING")

    def direct_report_download(self, report_id, file_id):
        # Retrieve the file metadata.
        report_file = self._service.files().get(reportId=report_id, fileId=file_id).execute()

        if report_file["status"] == "REPORT_AVAILABLE":
            # Create a get request.
            request = self._service.files().get_media(reportId=report_id, fileId=file_id)
            headers = request.headers
            headers.update({"Authorization": self.auth})
            r = requests.get(request.uri, stream=True, headers=headers)

            yield from r.iter_lines()
