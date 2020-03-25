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
import click

from io import StringIO

from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.utils.args import extract_args
from nck.streams.normalized_json_stream import NormalizedJSONStream
from nck.clients.sa360_client import SA360Client
from nck.helpers.sa360_helper import REPORT_TYPES

DATEFORMAT = "%Y-%m-%d"
ENCODING = "utf-8"


@click.command(name="read_sa360")
@click.option("--sa360-access-token", default=None)
@click.option("--sa360-client-id", required=True)
@click.option("--sa360-client-secret", required=True)
@click.option("--sa360-refresh-token", required=True)
@click.option("--sa360-agency-id", required=True)
@click.option("--sa360-advertiser-id", "sa360_advertiser_ids", required=True, multiple=True)
@click.option("--sa360-report-name", default="SA360 Report")
@click.option("--sa360-report-type", type=click.Choice(REPORT_TYPES), default=REPORT_TYPES[0])
@click.option(
    "--sa360-column", "sa360_columns", multiple=True, help="https://developers.google.com/search-ads/v2/report-types"
)
@click.option(
    "--sa360-custom-dimension",
    "sa360_custom_dimensions",
    multiple=True,
    help="https://developers.google.com/search-ads/v2/how-tos/reporting/custom-metrics-dimensions",
)
@click.option(
    "--sa360-custom-metric",
    "sa360_custom_metrics",
    multiple=True,
    help="https://developers.google.com/search-ads/v2/how-tos/reporting/custom-metrics-dimensions",
)
@click.option("--sa360-start-date", type=click.DateTime(), required=True)
@click.option("--sa360-end-date", type=click.DateTime(), required=True)
@processor("sa360_access_token", "sa360_refresh_token", "sa360_client_secret")
def sa360_reader(**kwargs):
    return SA360Reader(**extract_args("sa360_", kwargs))


class SA360Reader(Reader):
    def __init__(
        self,
        access_token,
        client_id,
        client_secret,
        refresh_token,
        agency_id,
        advertiser_ids,
        report_name,
        report_type,
        columns,
        custom_metrics,
        custom_dimensions,
        start_date,
        end_date,
    ):
        self.sa360_client = SA360Client(access_token, client_id, client_secret, refresh_token)
        self.agency_id = agency_id
        self.advertiser_ids = list(advertiser_ids)
        self.report_name = report_name
        self.report_type = report_type
        self.columns = list(columns)
        self.custom_metrics = list(custom_metrics)
        self.custom_dimensions = list(custom_dimensions)
        self.all_columns = self.columns + self.custom_dimensions + self.custom_metrics
        self.start_date = start_date
        self.end_date = end_date

    def format_response(self, report_generator):
        # skip headers in the CSV output
        next(report_generator)
        for row in report_generator:
            decoded_row = row.decode(ENCODING)
            csv_reader = csv.DictReader(StringIO(decoded_row), self.all_columns)
            yield next(csv_reader)

    def result_generator(self):
        advertiser_id = next((a for a in self.advertiser_ids), "")
        body = self.sa360_client.generate_report_body(
            self.agency_id,
            advertiser_id,
            self.report_type,
            self.columns,
            self.start_date,
            self.end_date,
            self.custom_dimensions,
            self.custom_metrics,
        )

        report_id = self.sa360_client.request_report_id(body)

        report_data = self.sa360_client.assert_report_file_ready(report_id)

        for report_generator in self.sa360_client.download_report_files(report_data, report_id):
            yield from self.format_response(report_generator)

    def read(self):
        yield NormalizedJSONStream("results" + "_".join(self.advertiser_ids), self.result_generator())
