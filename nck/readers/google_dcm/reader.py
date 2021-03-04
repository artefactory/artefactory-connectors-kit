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

from nck.readers.google_dcm.client import DCMClient
from nck.readers.google_dcm.config import ENCODING
from nck.readers.reader import Reader
from nck.streams.normalized_json_stream import NormalizedJSONStream


class GoogleDCMReader(Reader):
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
