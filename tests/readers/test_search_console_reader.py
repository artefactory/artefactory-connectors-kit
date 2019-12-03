import lib
import json
from datetime import datetime
from lib.readers.search_console_reader import SearchConsoleReader
from unittest import TestCase, mock


class SearchConsoleReaderTest(TestCase):
    DATEFORMAT = "%Y-%m-%d"

    @mock.patch("lib.readers.search_console_reader.MAX_END_DATE", datetime(2019, 2, 1))
    def test_get_end_date(self):
        end_date_lower = datetime(2019, 1, 1)
        end_date_greater = datetime(2019, 3, 1)
        assert SearchConsoleReader.get_end_date(end_date_lower) == end_date_lower
        assert SearchConsoleReader.get_end_date(end_date_greater) == lib.readers.search_console_reader.MAX_END_DATE

    @mock.patch("lib.readers.search_console_reader.SearchConsoleReader._run_query")
    def test_read(self, mock_query):
        kwargs = {
            "client_id": "",
            "client_secret": "",
            "access_token": "",
            "refresh_token": "",
            "dimensions": ("device",),
            "site_url": "",
            "start_date": datetime(2019, 1, 1),
            "end_date": datetime(2019, 1, 1),
            "date_column": False,
            "row_limit": "",
        }
        reader = SearchConsoleReader(**kwargs)

        def test_read_empty_data(mock_query):
            mock_query.return_value = [{"responseAgregationType": "byPage"}]
            if len(list(reader.read())) > 1:
                assert False, "Data is not empty"

        def test_format_data(mock_query):
            mock_query.return_value = [
                {"rows": [{"keys": ["MOBILE"], "clicks": 1, "impressions": 2}], "responseAgregationType": "byPage"},
                {"rows": [{"keys": ["DESKTOP"], "clicks": 3, "impressions": 4}], "responseAgregationType": "byPage"},
            ]

            expected = [
                {"device": "MOBILE", "clicks": 1, "impressions": 2},
                {"device": "DESKTOP", "clicks": 3, "impressions": 4},
            ]
            output_gen = (e for e in expected)

            for data in reader.read():
                for record, output in zip(data.readlines(), output_gen):
                    assert json.loads(record) == output

        def test_format_data_with_date_column(mock_query):
            kwargs["date_column"] = True
            reader = SearchConsoleReader(**kwargs)
            mock_query.return_value = [
                {"rows": [{"keys": ["MOBILE"], "clicks": 1, "impressions": 2}], "responseAgregationType": "byPage"},
                {"rows": [{"keys": ["DESKTOP"], "clicks": 3, "impressions": 4}], "responseAgregationType": "byPage"},
            ]

            expected = [
                {"date": "2019-01-01", "device": "MOBILE", "clicks": 1, "impressions": 2},
                {"date": "2019-01-01", "device": "DESKTOP", "clicks": 3, "impressions": 4},
            ]
            output_gen = (e for e in expected)

            for data in reader.read():
                for record, output in zip(data.readlines(), output_gen):
                    assert json.loads(record) == output

        test_read_empty_data(mock_query)
        test_format_data(mock_query)
        test_format_data_with_date_column(mock_query)
