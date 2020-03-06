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
from nck.streams.normalized_json_stream import NormalizedJSONStream
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
    ):
        self.dcm_client = DCMClient(access_token, client_id, client_secret, refresh_token)
        self.profile_ids = list(profile_ids)
        self.report_name = report_name
        self.report_type = report_type
        self.metrics = list(metrics)
        self.dimensions = list(dimensions)
        self.start_date = start_date
        self.end_date = end_date
        self.filters = list(filters)

    def format_response(self, report_generator):
        is_main_data = False

        for row in report_generator:
            decoded_row = row.decode(ENCODING)
            if decoded_row.startswith("Report Fields"):
                next(report_generator)
                decoded_row = next(report_generator).decode(ENCODING)
                is_main_data = True
            if decoded_row.startswith("Grand Total"):
                is_main_data = False

            if is_main_data:
                csv_reader = csv.DictReader(StringIO(decoded_row), self.dimensions + self.metrics)
                yield next(csv_reader)

    def result_generator(self):
        report = self.dcm_client.build_report_skeleton(self.report_name, self.report_type)
        self.dcm_client.add_report_criteria(report, self.start_date, self.end_date, self.metrics, self.dimensions)

        for profile_id in self.profile_ids:
            self.dcm_client.add_dimension_filters(report, profile_id, self.filters)

            report_id, file_id = self.dcm_client.run_report(report, profile_id)

            self.dcm_client.assert_report_file_ready(file_id=file_id, report_id=report_id)

            report_generator = self.dcm_client.direct_report_download(report_id, file_id)
            yield from self.format_response(report_generator)

    def read(self):
        yield DCMStream("results" + "_".join(self.profile_ids), self.result_generator())


class DCMStream(NormalizedJSONStream):
    DCM_PREFIX = "^dfa:"

    @staticmethod
    def _normalize_key(key):
        return re.split(DCMStream.DCM_PREFIX, key)[-1].replace(" ", "_").replace("-", "_")
