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
from ack.config import logger
from ack.readers.awin_advertiser.config import AWIN_API_ENDPOINT, DATEFORMAT, REPORT_TYPES
from ack.readers.reader import Reader
from ack.streams.json_stream import JSONStream
from ack.utils.retry import retry


class AwinAdvertiserReader(Reader):
    def __init__(
        self, auth_token, advertiser_id, report_type, region, campaign, timezone, interval, remove_tags, start_date, end_date
    ):
        self.auth_token = auth_token
        self.advertiser_id = advertiser_id
        self.report_type = report_type
        self.region = region
        self.campaign = campaign
        self.timezone = timezone
        self.interval = interval
        self.remove_tags = remove_tags
        self.start_date = start_date.strftime(DATEFORMAT)
        self.end_date = end_date.strftime(DATEFORMAT)

    @retry
    def request(self):
        build_url = f"{AWIN_API_ENDPOINT}{self.advertiser_id}/reports/{self.report_type}?"
        if self.report_type == REPORT_TYPES[0]:
            payload = {
                'startDate': self.start_date,
                'endDate': self.end_date,
                'timezone': self.timezone,
                'accessToken': self.auth_token
            }
        elif self.report_type == REPORT_TYPES[1]:
            payload = {
                'startDate': self.start_date,
                'endDate': self.end_date,
                'region': self.region,
                'timezone': self.timezone,
                'accessToken': self.auth_token
            }
        elif self.report_type == REPORT_TYPES[2]:
            payload = {
                'campaign': self.campaign,
                'interval': self.interval,
                'startDate': self.start_date,
                'endDate': self.end_date,
                'accessToken': self.auth_token
            }

        response = requests.get(
            build_url, params=payload
        )
        json_response = response.json()
        # there is no date in API response, add this in here
        for entry in json_response:
            if 'date' not in entry and self.start_date == self.end_date:
                entry['date'] = self.start_date

        # if report is not a campaign report, remove tags from the response
        if self.remove_tags and self.report_type != REPORT_TYPES[2]:
            for element in json_response:
                element.pop('tags')
        logger.debug(f"Response: {json_response}")
        return json_response

    def read(self):
        data = self.request()

        def result_generator():
            if data:
                yield from data
        yield JSONStream("results_", result_generator())
