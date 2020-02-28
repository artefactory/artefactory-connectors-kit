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
import csv
import re
from io import StringIO

import click
import logging

import requests

from click import ClickException
from tenacity import retry, wait_exponential, stop_after_delay

from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.utils.args import extract_args
from nck.streams.format_date_stream import FormatDateStream
from nck.clients.dcm_client import DCMClient
from nck.helpers.dcm_helper import REPORT_TYPES

logger = logging.getLogger("CM_client")

DATEFORMAT = "%Y-%m-%d"
ENCODING = "utf-8"


@click.command(name="read_dcm")
@click.option("--dcm-access-token", default=None)
@click.option("--dcm-client-id", required=True)
@click.option("--dcm-client-secret", required=True)
@click.option("--dcm-refresh-token", required=True)
@click.option("--dcm-profile-id", required=True)
@click.option("--dcm-report-name", default="DCM Report")
@click.option("--dcm-report-type", type=click.Choice(REPORT_TYPES), default=REPORT_TYPES[0])
@click.option(
    "--dcm-metric",
    "dcm_metrics",
    multiple=True,
    help="https://developers.google.com/doubleclick-advertisers/v3.3/dimensions/#standard-metrics",
)
@click.option(
    "--dcm-dimension",
    "dcm_dimensions",
    multiple=True,
    help="https://developers.google.com/doubleclick-advertisers/v3.3/dimensions/#standard-dimensions",
)
@click.option("--dcm-start-date", type=click.DateTime(), required=True)
@click.option("--dcm-end-date", type=click.DateTime(), required=True)
@click.option(
    "--dcm-filter",
    "dcm_filters",
    type=click.Tuple([str, str]),
    multiple=True,
    help="A filter is a tuple following this pattern: (dimensionName, dimensionValue). "
    "https://developers.google.com/doubleclick-advertisers/v3.3/dimensions/#standard-filters",
)
@click.option(
    "--dcm-date-format",
    default="%Y-%m-%d",
    help="And optional date format for the output stream. "
    "Follow the syntax of https://docs.python.org/3.8/library/datetime.html#strftime-strptime-behavior",
)
@processor("dcm_access_token", "dcm_refresh_token", "dcm_client_secret")
def dcm(**kwargs):
    return DcmReader(**extract_args("dcm_", kwargs))


class DcmReader(Reader):
    def __init__(
        self,
        access_token,
        client_id,
        client_secret,
        refresh_token,
        profile_id,
        report_name,
        report_type,
        metrics,
        dimensions,
        start_date,
        end_date,
        filters,
        date_format,
    ):
        self.dcm_client = DCMClient(access_token, client_id, client_secret, refresh_token)
        self.profile_id = profile_id
        self.report_name = report_name
        self.report_type = report_type
        self.metrics = list(metrics)
        self.dimensions = dimensions
        self.start_date = start_date
        self.end_date = end_date
        self.filters = list(filters)
        self.download_format = "CSV"
        self.date_format = date_format

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
            values = self.dcm_client._service.dimensionValues().query(profileId=profile_id, body=request).execute()

            report["criteria"]["dimensionFilters"] = report["criteria"].get("dimensionFilters", [])
            if values["items"]:
                # Add value as a filter to the report criteria.
                filter_value = next((val for val in values["items"] if val["value"] == dimension_value), {})
                if filter_value:
                    report["criteria"]["dimensionFilters"].append(filter_value)

    # @retry(wait=wait_exponential(multiplier=60, min=60, max=240), stop=stop_after_delay(3600))
    @retry(wait=wait_exponential(multiplier=1, min=1, max=4), stop=stop_after_delay(3600))
    def is_report_file_ready(self, report_id, file_id):
        """Poke the report file status"""
        report_file = self.dcm_client._service.files().get(reportId=report_id, fileId=file_id).execute()

        status = report_file["status"]
        if status == "REPORT_AVAILABLE":
            logger.info("File status is %s, ready to download." % status)
            return True
        elif status != "PROCESSING":
            raise ClickException("File status is %s, processing failed." % status)
        else:
            raise ClickException("File status is PROCESSING")

    def direct_download(self, report_id, file_id):
        # Retrieve the file metadata.
        report_file = self.dcm_client._service.files().get(reportId=report_id, fileId=file_id).execute()

        if report_file["status"] == "REPORT_AVAILABLE":
            # Create a get request.
            request = self.dcm_client._service.files().get_media(reportId=report_id, fileId=file_id)
            headers = request.headers
            headers.update({"Authorization": self.dcm_client.auth})
            r = requests.get(request.uri, stream=True, headers=headers)

            yield from r.iter_lines()

    def format_response(self, report_generator):
        is_main_data = False
        headers = []

        for row in report_generator:
            decoded_row = row.decode(ENCODING)
            if re.match("^Report Fields", decoded_row):
                decoded_row = next(report_generator).decode(ENCODING)
                headers = decoded_row.split(",")
                decoded_row = next(report_generator).decode(ENCODING)
                is_main_data = True
            if re.match("^Grand Total", decoded_row):
                is_main_data = False

            if is_main_data:
                csv_reader = csv.DictReader(StringIO(decoded_row), headers)
                yield next(csv_reader)

    def read(self):
        def result_generator():
            report = self.build_report_skeleton(self.report_name, self.report_type)
            self.add_report_criteria(report, self.start_date, self.end_date, self.metrics, self.dimensions)
            self.add_dimension_filters(report, self.profile_id, self.filters)

            inserted_report = (
                self.dcm_client._service.reports().insert(profileId=self.profile_id, body=report).execute()
            )

            report_id = inserted_report["id"]

            file = self.dcm_client._service.reports().run(profileId=self.profile_id, reportId=report_id).execute()

            file_id = file["id"]

            self.is_report_file_ready(file_id=file_id, report_id=report_id)
            yield from self.format_response(self.direct_download(report_id, file_id))

        # should replace results later by a good identifier
        yield FormatDateStream("results", result_generator(), keys=["Date"], date_format=self.date_format)
