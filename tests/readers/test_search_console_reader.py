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
from datetime import datetime
from nck.readers.search_console_reader import SearchConsoleReader
from unittest import TestCase, mock


class SearchConsoleReaderTest(TestCase):
    DATEFORMAT = "%Y-%m-%d"

    @mock.patch("nck.readers.search_console_reader.SearchConsoleReader._run_query")
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
            "date_range": None,
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
                    assert record == output

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
                    assert record == output

        test_read_empty_data(mock_query)
        test_format_data(mock_query)
        test_format_data_with_date_column(mock_query)
