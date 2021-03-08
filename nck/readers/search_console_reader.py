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
from oauth2client.client import GoogleCredentials
from oauth2client import GOOGLE_REVOKE_URI
from googleapiclient.discovery import build
import httplib2
from datetime import datetime, timedelta

import click
from nck.config import logger

from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.streams.json_stream import JSONStream
from nck.utils.args import extract_args
from nck.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS, build_date_range
from nck.utils.retry import retry


@click.command(name="read_search_console")
@click.option("--search-console-client-id", required=True)
@click.option("--search-console-client-secret", required=True)
@click.option("--search-console-access-token", default="")
@click.option("--search-console-refresh-token", required=True)
@click.option("--search-console-dimensions", required=True, multiple=True)
@click.option("--search-console-site-url", required=True)
@click.option("--search-console-start-date", type=click.DateTime(), default=None)
@click.option("--search-console-end-date", type=click.DateTime(), default=None)
@click.option("--search-console-date-column", type=click.BOOL, default=False)
@click.option("--search-console-row-limit", type=click.INT, default=25000)
@click.option(
    "--search-console-date-range",
    type=click.Choice(DEFAULT_DATE_RANGE_FUNCTIONS.keys()),
    help=f"One of the available NCK default date ranges: {DEFAULT_DATE_RANGE_FUNCTIONS.keys()}",
)
@processor()
def search_console(**params):
    return SearchConsoleReader(**extract_args("search_console_", params))


DATEFORMAT = "%Y-%m-%d"
# most recent data available is often 2 days ago.
MAX_END_DATE = datetime.today() - timedelta(days=2)


class SearchConsoleReader(Reader):
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
                token_uri="https://accounts.google.com/o/oauth2/token",
                user_agent=None,
                revoke_uri=GOOGLE_REVOKE_URI,
            )

            http = credentials.authorize(httplib2.Http())
            credentials.refresh(http)

            self._service = build(serviceName="webmasters", version="v3", credentials=credentials, cache_discovery=False)

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
