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
"""
   This was adapted from airflow google Base Hook.

   A base hook for Google cloud-related hooks. Google cloud has a shared REST
   API client that is built in the same way no matter which service you use.
   This class helps construct and authorize the credentials needed to then
   call googleapiclient.discovery.build() to actually discover and build a client
   for a Google cloud service.


    Three ways of authentication are supported:
   Default credentials: Only the 'Project Id' is required. You'll need to
   have set up default credentials, such as by the
   ``GOOGLE_APPLICATION_DEFAULT`` environment variable or from the metadata
   server on Google Compute Engine.
   JSON key file: Specify 'Project Id', 'Keyfile Path' and 'Scope'.
   Legacy P12 key files are not supported.
   JSON data provided the parameters
"""

from nck.config import logger
import json
import os
import google.auth
import google.oauth2.service_account

from typing import Dict, Optional, Sequence

_DEFAULT_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)  # type: Sequence[str]


class GoogleBaseClass:
    scopes = _DEFAULT_SCOPES

    def _get_credentials_and_project_id(self) -> google.auth.credentials.Credentials:
        """
        Returns the Credentials object for Google API and the associated project_id
        """
        key_path = os.environ.get("GCP_KEY_PATH")  # type: Optional[str]
        keyfile_dict = os.environ.get("GCP_KEY_JSON")  # type: Optional[str]
        if not key_path and not keyfile_dict:
            logger.info(
                "Getting connection using `google.auth.default()` "
                "since no key file is defined for hook."
                "You can pass a key as json in GCP_KEY_JSON "
                "or as a file in GCP_KEY_PATH"
            )
            credentials, project_id = google.auth.default(scopes=self.scopes)
        elif key_path:
            # Get credentials from a JSON file.
            if key_path.endswith(".json"):
                logger.debug(f"Getting connection using JSON key file {key_path}")
                credentials = google.oauth2.service_account.Credentials.from_service_account_file(key_path, scopes=self.scopes)
                project_id = credentials.project_id
            elif key_path.endswith(".p12"):
                raise Exception("Legacy P12 key file are not supported, " "use a JSON key file.")
            else:
                raise Exception("Unrecognised extension for key file.")
        else:
            # Get credentials from JSON data provided in the UI.
            try:
                assert keyfile_dict is not None
                keyfile_dict_json = json.loads(keyfile_dict)  # type: Dict[str, str]

                # Depending on how the JSON was formatted, it may contain
                # escaped newlines. Convert those to actual newlines.
                keyfile_dict_json["private_key"] = keyfile_dict_json["private_key"].replace("\\n", "\n")

                credentials = google.oauth2.service_account.Credentials.from_service_account_info(
                    keyfile_dict_json, scopes=self.scopes
                )
                project_id = credentials.project_id
            except json.decoder.JSONDecodeError:
                raise Exception("Invalid key JSON.")

        return credentials, project_id

    def _get_credentials(self) -> google.auth.credentials.Credentials:
        """
        Returns the Credentials object for Google API
        """
        credentials, _ = self._get_credentials_and_project_id()
        return credentials
