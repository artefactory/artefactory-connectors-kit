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
from typing import Dict

from nck.helpers.api_client_helper import get_dict_with_keys_converted_to_new_string_format

logger = logging.getLogger("ApiClient")


class ApiClient:
    API_VERSION = "v5"

    def __init__(self, token, language, skip_report_summary):
        self.token = token
        self.language = language
        self.skip_report_summary = skip_report_summary

    @staticmethod
    def get_formatted_request_body(
        str_format: str = "PascalCase",
        **request_body_elements
    ) -> Dict:
        return get_dict_with_keys_converted_to_new_string_format(
            request_body_elements,
            str_format
        )

    def execute_request(self, body):
        pass
