import click
import logging
import httplib2

import requests
import time
import datetime

from itertools import chain

from googleapiclient import discovery
from oauth2client import client, GOOGLE_REVOKE_URI

from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.utils.args import extract_args
from nck.streams.json_stream import JSONStream

from nck.utils.text import (
    get_generator_dict_from_str_csv,
    add_column_value_to_csv_line_iterator,
)

from nck.helpers.dbm_helper import POSSIBLE_REQUEST_TYPES, FILE_TYPES_DICT

DISCOVERY_URI = "https://analyticsreporting.googleapis.com/$discovery/rest"

default_start_date = datetime.date.today() - datetime.timedelta(days=2)
default_end_date = datetime.date.today()


@click.command(name="read_dbm")
@click.option("--dbm-access-token", default=None)
@click.option("--dbm-refresh-token", required=True)
@click.option("--dbm-client-id", required=True)
@click.option("--dbm-client-secret", required=True)
@click.option("--dbm-query-metric", multiple=True)
@click.option("--dbm-query-dimension", multiple=True)
@click.option("--dbm-request-type", type=click.Choice(POSSIBLE_REQUEST_TYPES))
@click.option("--dbm-query-id")
@click.option("--dbm-query-title")
@click.option("--dbm-query-frequency", default="ONE_TIME")
@click.option("--dbm-query-param-type", default="TYPE_TRUEVIEW")
@click.option("--dbm-filter", type=click.Tuple([str, int]), multiple=True)
@click.option("--dbm-file-type", multiple=True)
@click.option(
    "--dbm-day-range", required=True, default='LAST_7_DAYS',
    type=click.Choice(['PREVIOUS_DAY', 'LAST_30_DAYS', 'LAST_90_DAYS', 'LAST_7_DAYS'])
)
@processor("dbm_access_token", "dbm_refresh_token", "dbm_client_secret")
def dbm(**kwargs):
    # Should add validation argument in function of request_type
    return DbmReader(**extract_args("dbm_", kwargs))


class DbmReader(Reader):
    API_NAME = "doubleclickbidmanager"
    API_VERSION = "v1"

    def __init__(self, access_token, refresh_token, client_secret, client_id, **kwargs):
        credentials = client.GoogleCredentials(
            access_token,
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

        # API_SCOPES = ['https://www.googleapis.com/auth/doubleclickbidmanager']
        self._client = discovery.build(self.API_NAME, self.API_VERSION, http=http, cache_discovery=False)

        self.kwargs = kwargs

    def get_query(self, query_id, query_title):
        response = self._client.queries().listqueries().execute()
        if "queries" in response:
            for q in response["queries"]:
                if q["queryId"] == query_id or q["metadata"]["title"] == query_title:
                    return q
        else:
            logging.info(
                "No query found with the id {} or the title {}".format(
                    query_id, query_title
                )
            )
            return None

    def get_existing_query(self):
        query_id = self.kwargs.get("query_id", None)
        query_title = self.kwargs.get("query_title", None)
        query = self.get_query(query_id, query_id)
        if query:
            return query
        else:
            raise Exception(
                "No query found with the id {} or the title {}".format(
                    query_id, query_title
                )
            )

    def get_query_body(self):
        body_q = {
            "metadata": {
                "format": "CSV",
                "title": self.kwargs.get("query_title", "NO_TITLE_GIVEN"),
                "dataRange": self.kwargs.get('day_range', 'LAST_7_DAYS'),
            },
            "params": {
                "type": self.kwargs.get("query_param_type", 'TYPE_TRUEVIEW'),
                "groupBys": self.kwargs.get("query_dimension"),
                "metrics": self.kwargs.get("query_metric"),
                "filters": [
                    {"type": filt[0], "value": str(filt[1])}
                    for filt in self.kwargs.get("filter")
                ],
            },
            "schedule": {"frequency": self.kwargs.get("query_frequency", "ONE_TIME")},
        }
        return body_q

    def create_and_get_query(self):
        body_query = self.get_query_body()
        query = self._client.queries().createquery(body=body_query).execute()
        return query

    def get_query_report_url(self, existing_query=True):
        if existing_query:
            query_infos = self.get_existing_query()
        else:
            query_infos = self.create_and_get_query()
            query_id = query_infos["queryId"]
            while True:
                if not (query_infos["metadata"]["running"]):
                    break
                else:
                    logging.info(
                        "waiting for query of id : {} to complete running".format(query_id)
                    )
                    time.sleep(5)
                    query_infos = self.get_query(query_id, None)

        if query_infos["metadata"]["googleCloudStoragePathForLatestReport"]:
            url = query_infos["metadata"]["googleCloudStoragePathForLatestReport"]
        else:
            url = query_infos["metadata"]["googleDrivePathForLatestReport"]

        return url

    def get_generator_dict_from_str_csv(self, line_iterator):
        got_header = False
        headers = []
        for line in line_iterator:
            if got_header:
                headers = line.decode("utf-8").split(",")
            else:
                values = line.decode("utf-8").split(",")
                yield {headers[i]: values[i] for i in range(len(headers))}

    def get_query_report(self, existing_query=True):

        url = self.get_query_report_url(existing_query)
        report = requests.get(url, stream=True)
        return get_generator_dict_from_str_csv(report.iter_lines())

    def list_query_reports(self):
        reports_infos = self._client.reports().listreports(queryId=self.kwargs.get('query_id')).execute()
        for report in reports_infos["reports"]:
            yield report

    def get_lineitems_body(self):
        if len(self.kwargs.get("filter")) > 0:
            filter_types = [filt[0] for filt in self.kwargs.get("filter")]
            assert (
                    len(
                        [
                            filter_types[0] == filt
                            for filt in filter_types
                            if filter_types[0] == filt
                        ]
                    )
                    == 1
            ), "Lineitems accept just one filter type, multiple filter types detected"
            filter_ids = [str(filt[1]) for filt in self.kwargs.get("filter")]

            return {
                "filterType": filter_types[0],
                "filterIds": filter_ids,
                "format": "CSV",
                "fileSpec": "EWF",
            }
        else:
            return {}

    def get_lineitems_objects(self):
        body_lineitems = self.get_lineitems_body()
        response = (
            self._client.lineitems().downloadlineitems(body=body_lineitems).execute()
        )
        lineitems = response["lineItems"]
        lines = lineitems.split("\n")
        return get_generator_dict_from_str_csv(lines)

    def get_sdf_body(self):
        filter_types = [filt[0] for filt in self.kwargs.get("filter")]
        assert (
                len(
                    [
                        filter_types[0] == filt
                        for filt in filter_types
                        if filter_types[0] == filt
                    ]
                )
                == 1
        ), "sdf accept just one filter type, multiple filter types detected"
        filter_ids = [str(filt[1]) for filt in self.kwargs.get("filter")]

        file_types = self.kwargs.get("file_type")
        body_sdf = {
            "version": "4.2",
            "filterIds": filter_ids,
            "filterType": filter_types,
            "fileTypes": file_types,
        }
        return body_sdf

    def get_sdf_objects(self):
        body_sdf = self.get_sdf_body()
        file_types = body_sdf["fileTypes"]
        response = self._client.sdf().download(body=body_sdf).execute()

        return chain(
            *[
                get_generator_dict_from_str_csv(
                    add_column_value_to_csv_line_iterator(
                        response[FILE_TYPES_DICT[file_type]].split("\n"),
                        "file_type",
                        file_type,
                    )
                )
                for file_type in file_types
            ]
        )

    def read(self):
        # request existing query
        request_type = self.kwargs.get("request_type")
        if request_type == "existing_query":
            data = [self.get_existing_query()]
        elif request_type == "custom_query":
            data = [self.create_and_get_query()]
        elif request_type == "existing_query_report":
            data = self.get_query_report(existing_query=True)
        elif request_type == "custom_query_report":
            data = self.get_query_report(existing_query=False)
        elif request_type == "list_reports":
            data = self.list_query_reports()
        elif request_type == "lineitems_objects":
            data = self.get_lineitems_objects()
        elif request_type == "sdf_objects":
            data = self.get_sdf_objects()
        else:
            raise Exception('Unknown request type')

        def result_generator():
            for record in data:
                yield record

        # should replace results later by a good identifier
        yield JSONStream("results", result_generator())
