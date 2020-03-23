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
import logging
from typing import Dict, Any

from requests_toolbelt import sessions

from nck.helpers.api_client_helper import get_dict_with_keys_converted_to_new_string_format

logger = logging.getLogger("ApiClient")


class ApiClient:

    def __init__(self, token, base_url):
        self.token = token
        self.session = sessions.BaseUrlSession(base_url=base_url)

    @staticmethod
    def get_formatted_request_body(
        str_format: str = "PascalCase",
        **request_body_elements
    ) -> Dict:
        return get_dict_with_keys_converted_to_new_string_format(
            request_body_elements,
            str_format
        )

    def execute_request(
        self,
        method: str = "GET",
        url: str = "",
        body: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ):
        headers["Authorization"] = f"Bearer {self.token}"
        response = self.session.request(method, url, json=body, headers=headers)
        return response
