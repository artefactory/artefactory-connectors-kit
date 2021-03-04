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

import json
import os
import unittest
from unittest import mock

import nck.clients.google.client

MODULE_NAME = "nck.clients.google.client"


class TestGoogleCloudBaseClass(unittest.TestCase):
    def setUp(self):
        self.instance = nck.clients.google.client.GoogleClient()

    @mock.patch(MODULE_NAME + ".google.auth.default", return_value=("CREDENTIALS", "PROJECT_ID"))
    def test_get_credentials_and_project_id_with_default_auth(self, mock_auth_default):
        result = self.instance._get_credentials_and_project_id()
        mock_auth_default.assert_called_once_with(scopes=self.instance.scopes)
        self.assertEqual(("CREDENTIALS", "PROJECT_ID"), result)

    @mock.patch(
        MODULE_NAME + ".google.oauth2.service_account.Credentials" ".from_service_account_file",
        **{"return_value.project_id": "PROJECT_ID"}
    )
    @mock.patch.dict(os.environ, {"GCP_KEY_PATH": "KEY_PATH.json"})
    def test_get_credentials_and_project_id_with_service_account_file(self, mock_from_service_account_file):
        result = self.instance._get_credentials_and_project_id()
        mock_from_service_account_file.assert_called_once_with("KEY_PATH.json", scopes=self.instance.scopes)
        self.assertEqual((mock_from_service_account_file.return_value, "PROJECT_ID"), result)

    @mock.patch(MODULE_NAME + ".google.oauth2.service_account.Credentials" ".from_service_account_file")
    @mock.patch.dict(os.environ, {"GCP_KEY_PATH": "KEY_PATH.p12"})
    def test_get_credentials_and_project_id_with_service_account_file_and_p12_key(self, mock_from_service_account_file):
        with self.assertRaises(Exception):
            self.instance._get_credentials_and_project_id()

    @mock.patch(MODULE_NAME + ".google.oauth2.service_account.Credentials" ".from_service_account_file")
    @mock.patch.dict(os.environ, {"GCP_KEY_PATH": "KEY_PATH.unknown"})
    def test_get_credentials_and_project_id_with_service_account_file_and_unknown_key(self, mock_from_service_account_file):
        with self.assertRaises(Exception):
            self.instance._get_credentials_and_project_id()

    @mock.patch(
        MODULE_NAME + ".google.oauth2.service_account.Credentials" ".from_service_account_info",
        **{"return_value.project_id": "PROJECT_ID"}
    )
    @mock.patch.dict(os.environ, {"GCP_KEY_JSON": json.dumps({"private_key": "PRIVATE_KEY"})})
    def test_get_credentials_and_project_id_with_service_account_info(self, mock_from_service_account_file):
        result = self.instance._get_credentials_and_project_id()
        mock_from_service_account_file.assert_called_once_with({"private_key": "PRIVATE_KEY"}, scopes=self.instance.scopes)
        self.assertEqual((mock_from_service_account_file.return_value, "PROJECT_ID"), result)

    def test_default_scopes(self):
        self.assertEqual(self.instance.scopes, ("https://www.googleapis.com/auth/cloud-platform",))
