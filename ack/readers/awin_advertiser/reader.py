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

import requests
from urllib import request
from ack.readers.awin_advertiser.config import REPORT_TYPES
from ack.config import logger
from ack.readers.awin_advertiser.config import AWIN_API_ENDPOINT, DATEFORMAT
from ack.readers.reader import Reader
from ack.streams.json_stream import JSONStream
from ack.utils.retry import retry


class AwinAdvertiserReader(Reader):
    def __init__(
        self, auth_token, advertiser_id, report_type, region, timezone, start_date, end_date, **kwargs
    ):
        self.auth_token = auth_token
        self.advertiser_id = advertiser_id
        self.report_type = report_type
        self.region = region
        self.timezone = timezone
        self.start_date = start_date
        self.end_date = end_date
        self.download_format = "CSV"

    @retry
    def request(self):
        auth_token = self.auth_token
        advertiser_id = self.advertiser_id
        report_type = self.report_type
        region = self.region
        timezone = self.timezone
        start_date = self.start_date.strftime(DATEFORMAT)
        end_date = self.end_date.strftime(DATEFORMAT)

        if report_type == REPORT_TYPES[0]:
            build_url = f"{AWIN_API_ENDPOINT}{advertiser_id}"\
                f"/reports/publisher?startDate={start_date}&endDate={end_date}"\
                f"&timezone={timezone}&accessToken={auth_token}"
        elif report_type == REPORT_TYPES[1]:
            build_url = f"{AWIN_API_ENDPOINT}{advertiser_id}"\
                f"/reports/creative?startDate={start_date}&endDate={end_date}"\
                f"&region={region}&timezone={timezone}&accessToken={auth_token}"
        elif report_type == REPORT_TYPES[2]:
            build_url = f"{AWIN_API_ENDPOINT}{advertiser_id}"\
                f"/reports/campaign?startDate={start_date}&endDate={end_date}"\
                f"&accessToken={auth_token}"

        response = requests.get(
            build_url
        )
        json_response = response.json()
        logger.debug(f"Response: {json_response}")
        return json_response

    @staticmethod
    def create_date_range(start_date, end_date):
        return {"min": start_date.strftime(DATEFORMAT), "max": end_date.strftime(DATEFORMAT)}

    def read(self):
        data = self.request()

        def result_generator():
            if data:
                yield from data
        yield JSONStream("results_", result_generator())
