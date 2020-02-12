from unittest import TestCase, mock
import datetime

from nck.readers.googleads_reader import GoogleAdsReader, DATEFORMAT
from nck.helpers.googleads_helper import DATE_RANGE_TYPE_POSSIBLE_VALUES


class GoogleAdsReaderTest(TestCase):
    DATEFORMAT = "%Y%m%d"

    def mock_googleads_reader(self, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)

    kwargs = {
        "developer_token": "",
        "client_id": "",
        "client_secret": "",
        "refresh_token": "",
        "manager_id": "",
        "client_customer_ids": "",
        "report_name": "Custom Report",
        "report_type": "AD_PERFORMANCE_REPORT",
        "date_range_type": "LAST_7_DAYS",
        "start_date": "",
        "end_date": "",
        "download_format": "CSV",
        "fields": ("AdGroupName", "Date", "Impressions"),
        "report_filter": "",
        "include_zero_impressions": True,
    }

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_format_customer_id(self):
        input_id = 1234567890
        expected = "123-456-7890"
        assert GoogleAdsReader(**self.kwargs).format_customer_id(input_id) == expected

    @mock.patch("nck.readers.googleads_reader.GoogleAdsReader.fetch_report_from_gads_client_customer_obj")
    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_read_data(self, mock_query):
        reader = GoogleAdsReader(**self.kwargs)
        example_row1 = b'ad_group_example,2019-01-01,0'
        example_row2 = b'ad_group_example,2019-01-01,4'
        mock_query.stream_reader.return_value = [example_row1, example_row2]

        expected = [
            {
                "AdGroupName": "ad_group_example",
                "Date": "2019-01-01",
                "Impressions": "0"},
            {
                "AdGroupName": "ad_group_example",
                "Date": "2019-01-01",
                "Impressions": "4"}
        ]

        for data in reader.read():
            for record, output in zip(data.readlines(), iter(expected)):
                assert record == output

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_refuse_incorrect_id(self):
        """Test the function checking the Client Customer IDs
        format in order to refuse an invalid input
        """
        invalid_inputs = [
            '1231231234',
            '123_123_1234',
            'abc-abc-abcd',
            '1234-123-123',
        ]
        expected = None

        for invalid_input in invalid_inputs:
            assert GoogleAdsReader(**self.kwargs).valid_client_customer_id(invalid_input) == expected

    @staticmethod
    def get_report_definition(date_range_type):
        report_definition = {
            "reportName": "Custom Report",
            "dateRangeType": date_range_type,
            "reportType": "AD_GROUP_PERFORMANCES",
            "downloadFormat": "CSV",
            "selector": {"fields": ["AdGroupName", "Date", "Impressions"]},
        }
        return report_definition

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_add_invalid_custom_period_to_report_definition(self):
        """Test that report definition dateRangeType is replaced by default value
        when no start_date and end_date are provided
        """
        invalid_parameters = [
            {
                'date_range_type': "CUSTOM_DATE",
                'start_date': datetime.date(2019, 1, 1),
                'end_date': None,
            },
        ]
        expected_range_type = DATE_RANGE_TYPE_POSSIBLE_VALUES[0]

        for param in invalid_parameters:
            report_definition = self.get_report_definition(param['date_range_type'])

            temp_kwargs = self.kwargs
            temp_kwargs.update(param)
            GoogleAdsReader(**temp_kwargs).add_period_to_report_definition(report_definition)

            assert report_definition['dateRangeType'] == expected_range_type
            with self.assertRaises(KeyError):
                report_definition['start_date']
                report_definition['end_date']

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_add_valid_custom_period_to_report_definition(self):
        """Test that report definition dateRangeType is replaced by default value
        when no start_date and end_date are provided
        """

        valid_parameters = [
            {
                'date_range_type': "CUSTOM_DATE",
                'start_date': datetime.date(2019, 1, 1),
                'end_date': datetime.date(2021, 2, 1)
            },
        ]

        for param in valid_parameters:
            report_definition = self.get_report_definition(param['date_range_type'])
            expected_date_range = {
                "min": param['start_date'].strftime(DATEFORMAT),
                "max": param['end_date'].strftime(DATEFORMAT)
            }

            temp_kwargs = self.kwargs
            temp_kwargs.update(param)
            GoogleAdsReader(**temp_kwargs).add_period_to_report_definition(report_definition)

            assert report_definition['dateRangeType'] == param['date_range_type']
            assert report_definition['selector']['dateRange'] == expected_date_range

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_add_standard_period_to_report_definition(self):
        """Test that report definition dateRangeType is correctly implemented
        when user provide correct RangeType and parameters
        """

        valid_parameters = [
            {
                'date_range_type': "LAST_7_DAYS",
                'start_date': datetime.date(2019, 1, 1),
                'end_date': None
            },
            {
                'date_range_type': "LAST_30_DAYS",
                'start_date': None,
                'end_date': None
            },
        ]

        for param in valid_parameters:
            report_definition = self.get_report_definition(param['date_range_type'])

            temp_kwargs = self.kwargs
            temp_kwargs.update(param)
            GoogleAdsReader(**temp_kwargs).add_period_to_report_definition(report_definition)

            assert report_definition['dateRangeType'] == param['date_range_type']
            with self.assertRaises(KeyError):
                report_definition['start_date']
                report_definition['end_date']
