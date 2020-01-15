import click
import httplib2
import logging
import re

from datetime import datetime, timedelta
from click import ClickException
from googleapiclient import discovery
from oauth2client import client, GOOGLE_REVOKE_URI

from lib.commands.command import processor
from lib.readers.reader import Reader
from lib.utils.args import extract_args
from lib.utils.retry import retry
from lib.streams.normalized_json_stream import NormalizedJSONStream

DISCOVERY_URI = "https://analyticsreporting.googleapis.com/$discovery/rest"
DATEFORMAT = "%Y-%m-%d"


@click.command(name="read_ga")
@click.option("--ga-access-token", default=None)
@click.option("--ga-refresh-token", required=True)
@click.option("--ga-client-id", required=True)
@click.option("--ga-client-secret", required=True)
@click.option("--ga-view-id", type=click.STRING, default="")
@click.option("--ga-account-id", default=[], multiple=True)
@click.option("--ga-dimension", multiple=True)
@click.option("--ga-metric", multiple=True)
@click.option("--ga-start-date", type=click.DateTime(), default=None)
@click.option("--ga-end-date", type=click.DateTime(), default=None)
@click.option("--ga-date-range", nargs=2, type=click.DateTime(), default=None)
@click.option(
    "--ga-day-range", type=click.Choice(["PREVIOUS_DAY", "LAST_30_DAYS", "LAST_7_DAYS", "LAST_90_DAYS"]), default=None
)
@click.option("--ga-sampling-level", type=click.Choice(["SMALL", "DEFAULT", "LARGE"]), default="LARGE")
@processor("ga_access_token", "ga_refresh_token", "ga_client_secret")
def ga(**kwargs):
    # Should handle valid combinations dimensions/metrics in the API
    return GaReader(**extract_args("ga_", kwargs))


class GaReader(Reader):
    def __init__(self, access_token, refresh_token, client_id, client_secret, **kwargs):
        credentials = client.GoogleCredentials(
            access_token=access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            token_expiry=None,
            token_uri="https://accounts.google.com/o/oauth2/token",
            user_agent=None,
            revoke_uri=GOOGLE_REVOKE_URI,
        )

        http = credentials.authorize(httplib2.Http())
        credentials.refresh(http)
        self.client_v4 = discovery.build(
            "analytics", "v4", http=http, cache_discovery=False, discoveryServiceUrl=DISCOVERY_URI
        )
        self.client_v3 = discovery.build("analytics", "v3", http=http)
        self.kwargs = kwargs
        self.kwargs["credentials"] = credentials
        self.views_metadata = {}
        self.view_id = self.kwargs.get("view_id")
        self.date_range = self.get_date_range_for_ga_request()
        self.sampling_level = self.kwargs.get("sampling_level")

    def get_date_range_for_ga_request(self):
        start_date = self.kwargs.get("start_date")
        end_date = self.kwargs.get("end_date")
        date_range = self.kwargs.get("date_range")
        day_range = self.kwargs.get("day_range")

        if start_date and end_date:
            logging.info("ℹ️ Date format used for request : startDate and endDate")
            return self.create_date_range(start_date, end_date)
        elif date_range:
            logging.info("ℹ️ Date format used for request : dateRange")
            return self.create_date_range(date_range[0], date_range[1])
        elif day_range:
            logging.info("ℹ️ Date format used for request : dayRange")
            return self.generate_date_range_with_day_range(day_range)
        else:
            logging.warning("⚠️ No date range provided - Last 7 days by default ⚠️")
            return []

    def generate_date_range_with_day_range(self, day_range):
        days_delta = self.get_days_delta(day_range)
        current_day = datetime.now().date()
        d2 = current_day - timedelta(days=1)
        d1 = current_day - timedelta(days=days_delta)
        return self.create_date_range(d1, d2)

    @staticmethod
    def create_date_range(start_date, end_date):
        return {"startDate": start_date.strftime(DATEFORMAT), "endDate": end_date.strftime(DATEFORMAT)}

    @staticmethod
    def get_days_delta(day_range):
        delta_mapping = {"PREVIOUS_DAY": 1, "LAST_7_DAYS": 7, "LAST_30_DAYS": 30, "LAST_90_DAYS": 90}
        try:
            days_delta = delta_mapping[day_range]
        except KeyError:
            raise ClickException("{} is not handled by the reader".format(day_range))
        return days_delta

    def get_report_requests(self, view_ids):
        return [self.get_view_id_report_request(view_id) for view_id in view_ids]

    def get_view_id_report_request(self, view_id):
        metrics = self.kwargs.get("metric", [])
        dimensions = self.kwargs.get("dimension", [])
        report_request = {
            "viewId": view_id,
            "metrics": [{"expression": metric} for metric in metrics],
            "dimensions": [{"name": dimension} for dimension in dimensions],
            "pageSize": 50000,
            "samplingLevel": self.sampling_level,
        }
        if len(self.date_range) > 0:
            report_request["dateRanges"] = [self.date_range]
        return report_request

    @staticmethod
    def log_sampling(report):
        """ Log sampling data if a report has been sampled."""
        data = report.get("data", {})

        if data.get("samplesReadCounts") is not None:
            logging.warning("☝️Report has been sampled.")
            sample_reads = data["samplesReadCounts"][0]
            sample_space = data["samplingSpaceSizes"][0]
            logging.warning(f"sample reads : {sample_reads}")
            logging.warning(f"sample space :{sample_space}")

            logging.warning(f"sample percent :{100 * int(sample_reads) / int(sample_space)}%")
        else:
            logging.info("Report is not sampled.")

    @staticmethod
    def format_date(dateYYYYMMDD):
        return datetime.strptime(dateYYYYMMDD, "%Y%m%d").strftime(DATEFORMAT)

    @retry
    def _run_query(self):
        body = {"reportRequests": self.get_report_requests([self.view_id])}

        try:
            report_page = self.client_v4.reports().batchGet(body=body).execute()
            self.log_sampling(report_page["reports"][0])
            yield report_page["reports"][0]

            while "nextPageToken" in report_page["reports"][0]:
                page_token = report_page["reports"][0]["nextPageToken"]
                body["reportRequests"][0]["pageToken"] = page_token
                report_page = self.client_v4.reports().batchGet(body=body).execute()
                yield report_page["reports"][0]
        except Exception as e:
            raise ClickException("failed while requesting pages of the report: {}".format(e))

    @staticmethod
    def format_and_yield(report):
        dimension_names = report["columnHeader"]["dimensions"]
        metric_names = [m["name"] for m in report["columnHeader"]["metricHeader"]["metricHeaderEntries"]]
        for row in report["data"].get("rows", []):
            row_dimension_values = row["dimensions"]
            row_metric_values = row["metrics"][0]["values"]
            formatted_response = {}

            for dim, value in zip(dimension_names, row_dimension_values):
                formatted_response[dim] = value

            for metric, metric_value in zip(metric_names, row_metric_values):
                formatted_response[metric] = metric_value

            if "ga:date" in formatted_response:
                formatted_response["ga:date"] = GaReader.format_date(formatted_response["ga:date"])

            yield formatted_response

    def result_generator(self):
        for report in self._run_query():
            if "data" in report:
                yield from self.format_and_yield(report)
            else:
                return None

    def read(self):
        yield GaStream("result_view_" + self.view_id, self.result_generator())


class GaStream(NormalizedJSONStream):
    GA_PREFIX = "^ga:"

    @staticmethod
    def _normalize_key(key):
        return re.split(GaStream.GA_PREFIX, key)[-1].replace(" ", "_").replace("-", "_")
