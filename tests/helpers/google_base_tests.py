import unittest
import lib.helpers.google_base
from unittest import mock
import json
import os

MODULE_NAME = 'lib.helpers.google_base'


class TestGoogleCloudBaseClass(unittest.TestCase):
    def setUp(self):
        self.instance = lib.helpers.google_base.GoogleBaseClass()

    @mock.patch(MODULE_NAME + '.google.auth.default',
                return_value=("CREDENTIALS", "PROJECT_ID"))
    def test_get_credentials_and_project_id_with_default_auth(self, mock_auth_default):
        result = self.instance._get_credentials_and_project_id()
        mock_auth_default.assert_called_once_with(scopes=self.instance.scopes)
        self.assertEqual(('CREDENTIALS', 'PROJECT_ID'), result)

    @mock.patch(
        MODULE_NAME + '.google.oauth2.service_account.Credentials'
                      '.from_service_account_file',
        **{'return_value.project_id': "PROJECT_ID"}
    )
    @mock.patch.dict(os.environ, {'GCP_KEY_PATH': 'KEY_PATH.json'})
    def test_get_credentials_and_project_id_with_service_account_file(self,
                                                                      mock_from_service_account_file):
        result = self.instance._get_credentials_and_project_id()
        mock_from_service_account_file.assert_called_once_with('KEY_PATH.json',
                                                               scopes=self.instance.scopes)
        self.assertEqual((mock_from_service_account_file.return_value, 'PROJECT_ID'),
                         result)

    @mock.patch(
        MODULE_NAME + '.google.oauth2.service_account.Credentials'
                      '.from_service_account_file')
    @mock.patch.dict(os.environ, {'GCP_KEY_PATH': 'KEY_PATH.p12'})
    def test_get_credentials_and_project_id_with_service_account_file_and_p12_key(
            self,
            mock_from_service_account_file
    ):
        with self.assertRaises(Exception):
            self.instance._get_credentials_and_project_id()

    @mock.patch(
        MODULE_NAME + '.google.oauth2.service_account.Credentials'
                      '.from_service_account_file')
    @mock.patch.dict(os.environ, {'GCP_KEY_PATH': 'KEY_PATH.unknown'})
    def test_get_credentials_and_project_id_with_service_account_file_and_unknown_key(
            self,
            mock_from_service_account_file
    ):
        with self.assertRaises(Exception):
            self.instance._get_credentials_and_project_id()

    @mock.patch(
        MODULE_NAME + '.google.oauth2.service_account.Credentials'
                      '.from_service_account_info',
        **{'return_value.project_id': "PROJECT_ID"}
    )
    @mock.patch.dict(os.environ, {'GCP_KEY_JSON': json.dumps({
        'private_key': "PRIVATE_KEY"
    })})
    def test_get_credentials_and_project_id_with_service_account_info(self,
                                                                      mock_from_service_account_file):
        result = self.instance._get_credentials_and_project_id()
        mock_from_service_account_file.assert_called_once_with({
            'private_key': "PRIVATE_KEY"
        },
            scopes=self.instance.scopes)
        self.assertEqual((mock_from_service_account_file.return_value, 'PROJECT_ID'),
                         result)

    def test_default_scopes(self):
        self.assertEqual(self.instance.scopes,
                         ('https://www.googleapis.com/auth/cloud-platform',))
