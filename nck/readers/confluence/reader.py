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

import base64
from itertools import chain

import requests
from click import ClickException
from nck.readers.confluence.config import CONTENT_ENDPOINT, RECORDS_PER_PAGE
from nck.readers.confluence.helper import CUSTOM_FIELDS, parse_response
from nck.readers.reader import Reader
from nck.streams.json_stream import JSONStream


class ConfluenceReader(Reader):
    def __init__(self, user_login, api_token, atlassian_domain, content_type, spacekey, field):
        self.user_login = user_login
        self.api_token = api_token
        self._build_headers()
        self.atlassian_domain = atlassian_domain
        self.content_type = content_type
        self.spacekeys = list(spacekey)
        self.fields = list(field)

        self._validate_spacekeys()

    def _validate_spacekeys(self):
        requirements = [
            CUSTOM_FIELDS[field]["specific_to_spacekeys"]
            for field in self.fields
            if field in CUSTOM_FIELDS and "specific_to_spacekeys" in CUSTOM_FIELDS[field]
        ]
        if len(requirements) > 0:
            inter_requirements = (
                requirements[0] if len(requirements) == 1 else list(set(requirements[0]).intersection(*requirements[1:]))
            )
            if len(inter_requirements) == 0:
                raise ClickException("Invalid request. No intersection found between spacekey requirements.")
            elif self.spacekeys != inter_requirements:
                raise ClickException(f"Invalid request. Spacekeys should be set to '{inter_requirements}'.")

    def _build_headers(self):
        api_login = f"{self.user_login}:{self.api_token}"
        encoded_bytes = base64.b64encode(api_login.encode("utf-8"))
        encoded_string = str(encoded_bytes, "utf-8")
        self.headers = {"Authorization": f"Basic {encoded_string}", "Content-Type": "application/json"}

    def _build_params(self):
        api_fields = [CUSTOM_FIELDS[field]["source_field"] if field in CUSTOM_FIELDS else field for field in self.fields]
        return {"type": self.content_type, "expand": ",".join(api_fields)}

    def _get_raw_response(self, page_nb, spacekey=None):
        params = self._build_params()
        params["start"] = page_nb * RECORDS_PER_PAGE
        params["limit"] = RECORDS_PER_PAGE
        if spacekey is not None:
            params["spaceKey"] = spacekey

        url = f"{self.atlassian_domain}/{CONTENT_ENDPOINT}"
        response = requests.get(url, headers=self.headers, params=params)
        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def _get_report_generator(self, spacekey=None):
        page_nb = 0
        raw_response = self._get_raw_response(page_nb, spacekey)
        all_responses = [parse_response(raw_response, self.fields)]

        while raw_response["_links"].get("next"):
            page_nb += 1
            raw_response = self._get_raw_response(page_nb, spacekey)
            all_responses.append(parse_response(raw_response, self.fields))

        return chain(*all_responses)

    def _get_aggregated_report_generator(self):
        if self.spacekeys:
            for spacekey in self.spacekeys:
                yield from self._get_report_generator(spacekey)
        else:
            yield from self._get_report_generator()

    def read(self):
        yield JSONStream("results_", self._get_aggregated_report_generator())
