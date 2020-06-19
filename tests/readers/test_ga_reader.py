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
from unittest import TestCase, mock
from click import ClickException

from nck.readers.ga_reader import GaReader, GaStream


class GaReaderTest(TestCase):
    DATEFORMAT = "%Y-%m-%d"

    def mock_ga_reader(self, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)

    def test_normalized_ga_stream(self):
        rows = [{"ga:date": 0, "ga:dimension": "dim", "ga:metric": "met"}, {"ga:date-date": 0}, {"ga:date date": 0}]
        expected = [{"date": 0, "dimension": "dim", "metric": "met"}, {"date_date": 0}, {"date_date": 0}]
        ga_stream = GaStream("stream", iter(rows))
        for row, output in zip(ga_stream.readlines(), iter(expected)):
            assert row == output

    def test_format_date(self):
        test_date = "20190101"
        wrong_date = "01/01/2019"
        assert GaReader.format_date(test_date) == "2019-01-01"
        self.assertRaises(ValueError, GaReader.format_date, wrong_date)

    def test_get_days_delta(self):
        inputs = ["PREVIOUS_DAY", "LAST_7_DAYS", "LAST_30_DAYS", "LAST_90_DAYS"]
        expected = [1, 7, 30, 90]
        output = [GaReader.get_days_delta(input) for input in inputs]
        assert output == expected
        fail = "PVRIOUES_DAY"
        self.assertRaises(ClickException, GaReader.get_days_delta, fail)

    @mock.patch("nck.readers.ga_reader.GaReader._run_query")
    @mock.patch.object(GaReader, "__init__", mock_ga_reader)
    def test_read(self, mock_query):

        kwargs = {
            "dimensions": ("date",),
            "metric": (),
            "start_date": datetime(2019, 1, 1),
            "view_ids": ["0", "1"],
            "end_date": datetime(2019, 1, 1),
            "add_view": False
        }
        reader = GaReader(**kwargs)
        kwargs["add_view"] = True
        reader_with_view_id = GaReader(**kwargs)

        format_data_return_value = [
            {
                "columnHeader": {
                    "dimensions": ["ga:date"],
                    "metricHeader": {"metricHeaderEntries": [{"name": "ga:users", "type": "INTEGER"}]},
                },
                "data": {
                    "rows": [{"dimensions": ["20190101"], "metrics": [{"values": ["2"]}]}],
                    "isDataGolden": True,
                },
            },
            {
                "columnHeader": {
                    "dimensions": ["ga:date"],
                    "metricHeader": {"metricHeaderEntries": [{"name": "ga:newUsers", "type": "INTEGER"}]},
                },
                "data": {
                    "rows": [{"dimensions": ["20190101"], "metrics": [{"values": ["1"]}]}],
                    "isDataGolden": True,
                },
            },
        ]

        def test_read_empty_data(mock_query):
            mock_query.return_value = [{"data": {"isDataGolden": True}}]
            if len(list(reader.read())) > 1:
                assert False, "Data is not empty"

        def test_format_data(mock_query):
            mock_query.return_value = format_data_return_value

            expected = [
                {"date": "2019-01-01", "users": "2"}, {"date": "2019-01-01", "newUsers": "1"},
                {"date": "2019-01-01", "users": "2"}, {"date": "2019-01-01", "newUsers": "1"}
            ]

            for data in reader.read():
                for record, output in zip(data.readlines(), iter(expected)):
                    assert record == output

        def test_format_data_and_view_id(mock_query):
            mock_query.return_value = format_data_return_value

            expected = [
                {"viewId": "0", "date": "2019-01-01", "users": "2"},
                {"viewId": "0", "date": "2019-01-01", "newUsers": "1"},
                {"viewId": "1", "date": "2019-01-01", "users": "2"},
                {"viewId": "1", "date": "2019-01-01", "newUsers": "1"}
            ]

            for data in reader_with_view_id.read():
                for record, output in zip(data.readlines(), iter(expected)):
                    assert record == output

        test_read_empty_data(mock_query)
        test_format_data(mock_query)
        test_format_data_and_view_id(mock_query)
