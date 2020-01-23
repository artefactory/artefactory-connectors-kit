from datetime import datetime
from unittest import TestCase, mock
from click import ClickException

from lib.readers.ga_reader import GaReader, GaStream


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

    @mock.patch("lib.readers.ga_reader.GaReader._run_query")
    @mock.patch.object(GaReader, "__init__", mock_ga_reader)
    def test_read(self, mock_query):

        kwargs = {
            "dimensions": ("date",),
            "metric": (),
            "start_date": datetime(2019, 1, 1),
            "view_id": "0",
            "end_date": datetime(2019, 1, 1),
        }
        reader = GaReader(**kwargs)

        def test_read_empty_data(mock_query):
            mock_query.return_value = [{"data": {"isDataGolden": True}}]
            if len(list(reader.read())) > 1:
                assert False, "Data is not empty"

        def test_format_data(mock_query):
            mock_query.return_value = [
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

            expected = [{"date": "2019-01-01", "users": "2"}, {"date": "2019-01-01", "newUsers": "1"}]

            for data in reader.read():
                for record, output in zip(data.readlines(), iter(expected)):
                    assert record == output

        test_read_empty_data(mock_query)
        test_format_data(mock_query)
