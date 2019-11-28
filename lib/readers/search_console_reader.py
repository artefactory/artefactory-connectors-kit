from oauth2client.client import GoogleCredentials
from oauth2client import GOOGLE_REVOKE_URI
from googleapiclient.discovery import build
import httplib2
from datetime import datetime, timedelta

import click
import logging

from lib.commands.command import processor
from lib.readers.reader import Reader
from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.utils.args import extract_args
from lib.utils.retry import retry


@click.command(name="read_search_console")
@click.option("--search-client-id", required=True)
@click.option("--search-client-secret", required=True)
@click.option("--search-access-token", required=True)
@click.option("--search-refresh-token", required=True)
@click.option("--search-dimensions", required=True, multiple=True)
@click.option("--search-site-url", required=True)
@click.option("--search-start-date", type=click.DateTime(), default=None)
@click.option("--search-end-date", type=click.DateTime(), default=None)
@click.option("--search-date-column", "-d", type=click.BOOL, default=False)
@processor()
def search_console(**params):
    return SearchConsoleReader(**extract_args("search_", params))


DATEFORMAT = "%Y-%m-%d"
# most recent data available is 3days ago.
DEFAULT_END_DATE = datetime.now() - timedelta(days=3)


class SearchConsoleReader(Reader):

    # max returned rows per query.
    ROWS_LIMIT = 25000

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
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.dimensions = list(dimensions)
        self.site_url = site_url
        self.start_date = datetime.strftime(start_date, DATEFORMAT)
        self.end_date = datetime.strftime(self.get_end_date(end_date), DATEFORMAT)
        self.with_date_column = date_column and (self.start_date == self.end_date)

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

            self._service = build(
                serviceName="webmasters", version="v3", credentials=credentials, cache_discovery=False
            )

    @staticmethod
    def get_end_date(end_date):
        return min(DEFAULT_END_DATE, end_date)

    def build_query(self):

        query = {
            "startDate": self.start_date,
            "endDate": self.end_date,
            "dimensions": self.dimensions,
            "startRow": self.start_row,
            "rowLimit": self.ROWS_LIMIT,
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
            logging.info("{} lines successfully processed...".format(len(response.get("rows")) + self.start_row))
            self.start_row += self.ROWS_LIMIT
            response = self._service.searchanalytics().query(siteUrl=self.site_url, body=self.build_query()).execute()
            yield response

    def read(self):
        for data in self._run_query():

            if len(data.get("rows", [])):

                def result_generator(data):
                    data_keys = [*data["rows"][0]]
                    metric_names = data_keys[1:]

                    for report in data.get("rows", []):
                        record = {}
                        keys = report.get("keys", [])

                        for dimension, key in zip(self.dimensions, keys):
                            if self.with_date_column:
                                record["date"] = self.start_date
                            record[dimension] = key

                        for metric in metric_names:
                            record[metric] = report.get(metric, "")

                        yield record

                yield NormalizedJSONStream("search_console_results", result_generator(data))
