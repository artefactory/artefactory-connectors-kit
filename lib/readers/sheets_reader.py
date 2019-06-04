# import json
# import logging
# import os
# from config import config
#
# import click
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
#
# from lib.commands.execute import app_default_options
# from lib.readers.reader import BaseReader
# from lib.streams.json_stream import JSONStream
#
#
# @click.command(name="sheets")
# @click.option("--sheets-credentials", required=True)
# @click.option("--sheets-file-url", required=True)
# @app_default_options
# def sheets(**kwargs):
#     credentials_path = os.path.join(config.get("SECRETS_PATH"), kwargs.get("sheets_credentials"))
#     with open(credentials_path) as json_file:
#         credentials_dict = json.loads(json_file.read())
#         return SheetsReader(
#             credentials_dict,
#             kwargs.get("sheets_file_url")
#         )
#
#
# class SheetsReader(BaseReader):
#
#     _stream = JSONStream
#     _scopes = ['https://spreadsheets.google.com/feeds',
#                'https://www.googleapis.com/auth/drive']
#     _client = None
#     _credentials = None
#
#     def __init__(self, credentials, file_url=None):
#         self._credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scopes=self._scopes)
#         self._file_url = file_url
#
#     def read(self, element):
#         sheet = self._client.open_by_url(element).sheet1
#         results = sheet.get_all_records()
#         return sheet.title, results
#
#     def connect(self):
#         self._client = gspread.authorize(self._credentials)
#
#     def close(self):
#         pass
#
#     def list(self):
#         return [self._file_url]
