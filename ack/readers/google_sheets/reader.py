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

import gspread
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
from ack.readers.reader import Reader
from ack.streams.json_stream import JSONStream


class GoogleSheetsReader(Reader):
    _scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(
        self,
        project_id: str,
        private_key_id: str,
        private_key: str,
        client_email: str,
        client_id: str,
        client_cert: str,
        sheet_key: str,
        page_number: int,
    ):
        self._sheet_key = sheet_key
        self._page_number = page_number
        credentials = self.__init_credentials(project_id, private_key_id, private_key, client_email, client_id, client_cert)
        scoped_credentials = credentials.with_scopes(self._scopes)
        self._gc = gspread.Client(auth=scoped_credentials)
        self._gc.session = AuthorizedSession(scoped_credentials)

    def __init_credentials(self, project_id, private_key_id, private_key, client_email, client_id, client_cert):
        keyfile_dict = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key.replace("\\n", "\n"),
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "client_email": client_email,
            "client_id": client_id,
            "client_x509_cert_url": client_cert,
            "token_uri": "https://accounts.google.com/o/oauth2/token",
        }
        return service_account.Credentials.from_service_account_info(info=keyfile_dict)

    def read(self):
        sheet = self._gc.open_by_key(self._sheet_key).get_worksheet(self._page_number)
        list_of_hashes = sheet.get_all_records()

        def result_generator():
            for record in list_of_hashes:
                yield record

        yield JSONStream("gsheet", result_generator())
