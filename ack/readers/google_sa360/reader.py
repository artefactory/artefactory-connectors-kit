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

from ack.clients.google_sa360.client import GoogleSA360Client
from ack.readers.reader import Reader
from ack.streams.json_stream import JSONStream
from ack.utils.date_handler import build_date_range
from ack.utils.text import get_report_generator_from_flat_file


class GoogleSA360Reader(Reader):
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
        saved_columns,
        start_date,
        end_date,
        date_range,
    ):
        self.sa360_client = GoogleSA360Client(access_token, client_id, client_secret, refresh_token)
        self.agency_id = agency_id
        self.advertiser_ids = list(advertiser_ids)
        self.report_name = report_name
        self.report_type = report_type
        self.columns = list(columns)
        self.saved_columns = list(saved_columns)
        self.all_columns = self.columns + self.saved_columns
        self.start_date, self.end_date = build_date_range(start_date, end_date, date_range)

    def result_generator(self):
        for advertiser_id in self.advertiser_ids:
            body = self.sa360_client.generate_report_body(
                self.agency_id,
                advertiser_id,
                self.report_type,
                self.columns,
                self.start_date,
                self.end_date,
                self.saved_columns,
            )

            report_id = self.sa360_client.request_report_id(body)

            report_data = self.sa360_client.assert_report_file_ready(report_id)

            for line_iterator in self.sa360_client.download_report_files(report_data, report_id):
                yield from get_report_generator_from_flat_file(line_iterator)

    def read(self):
        if not self.advertiser_ids:
            self.advertiser_ids = self.sa360_client.get_all_advertisers_of_agency(self.agency_id)

        yield JSONStream("results" + "_".join(self.advertiser_ids), self.result_generator())
