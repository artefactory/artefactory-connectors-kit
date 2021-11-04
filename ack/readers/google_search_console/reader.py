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

from datetime import datetime, timedelta

import httplib2
from googleapiclient.discovery import build
from ack.config import logger
from ack.readers.google_search_console.config import DATEFORMAT, GOOGLE_TOKEN_URI
from ack.readers.reader import Reader
from ack.streams.json_stream import JSONStream
from ack.utils.date_handler import build_date_range
from ack.utils.retry import retry
from oauth2client import GOOGLE_REVOKE_URI
from oauth2client.client import GoogleCredentials

# Most recent data available is often 2 days ago
MAX_END_DATE = datetime.today() - timedelta(days=2)


class GoogleSearchConsoleReader(Reader):
    def __init__(
        self,
        client_id,
        client_secret,
        access_token,
        refresh_token,
        dimensions,
        site_url,
        start_date,
        end_date,
        date_column,
        row_limit,
        date_range,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.dimensions = list(dimensions)
        self.site_url = site_url
        self.start_date, self.end_date = build_date_range(start_date, end_date, date_range)
        self.with_date_column = date_column
        self.row_limit = row_limit

        self._service = None
        self.is_api_ready = False
        self.start_row = 0

    def initialize_analyticsreporting(self):
        if not self.is_api_ready:
            credentials = GoogleCredentials(
                access_token=self.access_token,
                client_id=self.client_id,
                client_secret=self.client_secret,
                refresh_token=self.refresh_token,
                token_expiry=None,
                token_uri=GOOGLE_TOKEN_URI,
                user_agent=None,
                revoke_uri=GOOGLE_REVOKE_URI,
            )

            http = credentials.authorize(httplib2.Http())
            credentials.refresh(http)

            self._service = build(serviceName="searchconsole", version="v1", credentials=credentials, cache_discovery=False)

    @staticmethod
    def check_end_date(end_date):
        if end_date > MAX_END_DATE:
            logger.warning(f"The most recent date you can request is {datetime.strftime(MAX_END_DATE, DATEFORMAT)}")
        return end_date

    def build_query(self):

        query = {
            "startDate": datetime.strftime(self.start_date, DATEFORMAT),
            "endDate": datetime.strftime(self.check_end_date(self.end_date), DATEFORMAT),
            "dimensions": self.dimensions,
            "startRow": self.start_row,
            "rowLimit": self.row_limit,
            "searchType": "web",
            "responseAggregationType": "byPage",
        }

        return query

    @retry
    def _run_query(self):
        self.initialize_analyticsreporting()

        response = self._service.searchanalytics().query(siteUrl=self.site_url, body=self.build_query()).execute()
        yield response

        # Pagination
        while len(response.get("rows", [])) != 0:
            logger.info(f"{len(response.get('rows')) + self.start_row} lines successfully processed...")
            self.start_row += self.row_limit
            response = self._service.searchanalytics().query(siteUrl=self.site_url, body=self.build_query()).execute()
            yield response

    def format_and_yield(self, data):
        data_keys = [*data["rows"][0]]
        metric_names = data_keys[1:]
        for report in data.get("rows", []):
            record = {}
            keys = report.get("keys", [])

            for dimension, key in zip(self.dimensions, keys):
                if self.with_date_column:
                    record["date"] = datetime.strftime(self.start_date, DATEFORMAT)
                record[dimension] = key

            for metric in metric_names:
                record[metric] = report.get(metric, "")

            yield record

    def result_generator(self):
        for data in self._run_query():
            if len(data.get("rows", [])):
                yield from self.format_and_yield(data)
            else:
                return None

    def read(self):
        yield JSONStream("search_console_results", self.result_generator())
