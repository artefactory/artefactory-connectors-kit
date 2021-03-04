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

import re
from datetime import datetime, timedelta

import httplib2
from click import ClickException
from googleapiclient import discovery
from nck.config import logger
from nck.readers.google_analytics.config import DATEFORMAT, DISCOVERY_URI, GOOGLE_TOKEN_URI
from nck.readers.reader import Reader
from nck.streams.normalized_json_stream import NormalizedJSONStream
from nck.utils.retry import retry
from oauth2client import GOOGLE_REVOKE_URI, client


class GoogleAnalyticsReader(Reader):
    def __init__(self, access_token, refresh_token, client_id, client_secret, **kwargs):
        credentials = client.GoogleCredentials(
            access_token=access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            token_expiry=None,
            token_uri=GOOGLE_TOKEN_URI,
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
        self.view_ids = self.kwargs.get("view_id")
        self.date_range = self.get_date_range_for_ga_request()
        self.sampling_level = self.kwargs.get("sampling_level")
        self.add_view = self.kwargs.get("add_view", False)

    def get_date_range_for_ga_request(self):
        start_date = self.kwargs.get("start_date")
        end_date = self.kwargs.get("end_date")
        date_range = self.kwargs.get("date_range")
        day_range = self.kwargs.get("day_range")

        if start_date and end_date:
            logger.info("Date format used for request : startDate and endDate")
            return self.create_date_range(start_date, end_date)
        elif date_range:
            logger.info("Date format used for request : dateRange")
            return self.create_date_range(date_range[0], date_range[1])
        elif day_range:
            logger.info("Date format used for request : dayRange")
            return self.generate_date_range_with_day_range(day_range)
        else:
            logger.warning("No date range provided - Last 7 days by default")
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
            raise ClickException(f"{day_range} is not handled by the reader")
        return days_delta

    def get_view_id_report_request(self, view_id):
        metrics = self.kwargs.get("metric", [])
        dimensions = self.kwargs.get("dimension", [])
        segment_ids = self.kwargs.get("segment_id", [])
        report_request = {
            "viewId": view_id,
            "metrics": [{"expression": metric} for metric in metrics],
            "dimensions": [{"name": dimension} for dimension in dimensions],
            "segments": [{"segmentId": segment_id} for segment_id in segment_ids],
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
            logger.warning("☝️Report has been sampled.")
            sample_reads = data["samplesReadCounts"][0]
            sample_space = data["samplingSpaceSizes"][0]
            logger.warning(f"sample reads : {sample_reads}")
            logger.warning(f"sample space :{sample_space}")

            logger.warning(f"sample percent :{100 * int(sample_reads) / int(sample_space)}%")
        else:
            logger.info("Report is not sampled.")

    @staticmethod
    def format_date(dateYYYYMMDD):
        return datetime.strptime(dateYYYYMMDD, "%Y%m%d").strftime(DATEFORMAT)

    @retry
    def _run_query(self, view_id):
        body = {"reportRequests": self.get_view_id_report_request(view_id)}

        try:
            report_page = self.client_v4.reports().batchGet(body=body).execute()
            self.log_sampling(report_page["reports"][0])
            yield report_page["reports"][0]

            while "nextPageToken" in report_page["reports"][0]:
                page_token = report_page["reports"][0]["nextPageToken"]
                body["reportRequests"]["pageToken"] = page_token
                report_page = self.client_v4.reports().batchGet(body=body).execute()
                yield report_page["reports"][0]
        except Exception as e:
            raise ClickException(f"failed while requesting pages of the report: {e}")

    def format_and_yield(self, view_id, report):
        dimension_names = report["columnHeader"]["dimensions"]
        metric_names = [m["name"] for m in report["columnHeader"]["metricHeader"]["metricHeaderEntries"]]
        for row in report["data"].get("rows", []):
            row_dimension_values = row["dimensions"]
            row_metric_values = row["metrics"][0]["values"]
            formatted_response = {}

            if self.add_view:
                formatted_response["ga:viewId"] = view_id

            for dim, value in zip(dimension_names, row_dimension_values):
                formatted_response[dim] = value

            for metric, metric_value in zip(metric_names, row_metric_values):
                formatted_response[metric] = metric_value

            if "ga:date" in formatted_response:
                formatted_response["ga:date"] = GoogleAnalyticsReader.format_date(formatted_response["ga:date"])

            yield formatted_response

    def result_generator(self):
        for view_id in self.view_ids:
            for report in self._run_query(view_id):
                if "data" in report:
                    yield from self.format_and_yield(view_id, report)

    def read(self):
        yield GaStream("result_view_" + "_".join(self.view_ids), self.result_generator())


class GaStream(NormalizedJSONStream):
    GA_PREFIX = "^ga:"

    @staticmethod
    def _normalize_key(key):
        return re.split(GaStream.GA_PREFIX, key)[-1].replace(" ", "_").replace("-", "_")
