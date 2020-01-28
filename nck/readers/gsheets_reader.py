import click
import gspread
from oauth2client.client import GoogleCredentials

from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.utils.args import extract_args
from nck.streams.normalized_json_stream import NormalizedJSONStream


@click.command(name="read_gsheets")
@click.option("--gsheets-url", required=True)
@click.option("--gsheets-worksheet-name", required=True, multiple=True)
@processor()
def gsheets(**kwargs):
    return GSheetsReader(**extract_args("gsheets_", kwargs))


class GSheetsReader(Reader):

    _scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self, url, sheet_name):
        credentials = GoogleCredentials.get_application_default()
        self._credentials = credentials.create_scoped(self._scopes)
        self._url = url
        self._sheet_name = sheet_name

    def read(self):

        client = gspread.authorize(self._credentials)
        spreadsheet = client.open_by_url(self._url)

        for _sheet_name in self._sheet_name:

            worksheet = spreadsheet.worksheet(_sheet_name)

            def result_generator():
                for record in worksheet.get_all_records():
                    yield record

            yield NormalizedJSONStream(worksheet.title, result_generator())
