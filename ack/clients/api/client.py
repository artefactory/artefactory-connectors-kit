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

from typing import Any, Dict

from requests_toolbelt import sessions


class ApiClient:
    def __init__(self, token, base_url):
        self.token = token
        self.session = sessions.BaseUrlSession(base_url=base_url)

    def execute_request(
        self,
        method: str = "GET",
        url: str = "",
        body: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        stream: bool = False,
    ):
        headers["Authorization"] = f"Bearer {self.token}"
        response = self.session.request(method, url, json=body, headers=headers)
        return response
