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
import click

from io import StringIO

from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.utils.args import extract_args
from nck.streams.format_date_stream import FormatDateStream
from nck.clients.dcm_client import DCMClient
from nck.helpers.dcm_helper import REPORT_TYPES

DATEFORMAT = "%Y-%m-%d"
ENCODING = "utf-8"


@click.command(name="read_dcm")
@click.option("--dcm-access-token", default=None)
@click.option("--dcm-client-id", required=True)
@click.option("--dcm-client-secret", required=True)
@click.option("--dcm-refresh-token", required=True)
@click.option("--dcm-profile-id", "dcm_profile_ids", required=True, multiple=True)
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
        profile_ids,
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
        self.profile_ids = list(profile_ids)
        self.report_name = report_name
        self.report_type = report_type
        self.metrics = list(metrics)
        self.dimensions = dimensions
        self.start_date = start_date
        self.end_date = end_date
        self.filters = list(filters)
        self.date_format = date_format

    @staticmethod
    def format_response(report_generator):
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

    def result_generator(self):
        report = self.dcm_client.build_report_skeleton(self.report_name, self.report_type)
        self.dcm_client.add_report_criteria(report, self.start_date, self.end_date, self.metrics, self.dimensions)

        for profile_id in self.profile_ids:
            self.dcm_client.add_dimension_filters(report, profile_id, self.filters)

            report_id, file_id = self.dcm_client.run_report(report, profile_id)

            is_ready = self.dcm_client.is_report_file_ready(file_id=file_id, report_id=report_id)

            if is_ready:
                report_generator = self.dcm_client.direct_report_download(report_id, file_id)
                yield from self.format_response(report_generator)

    def read(self):
        # should replace results later by a good identifier
        yield FormatDateStream("results", self.result_generator(), keys=["Date"], date_format=self.date_format)
