from unittest import TestCase, mock
from parameterized import parameterized
import datetime
from click import ClickException

from nck.readers.googleads_reader import GoogleAdsReader, DATEFORMAT
from nck.helpers.googleads_helper import DATE_RANGE_TYPE_POSSIBLE_VALUES


def mock_query(*args, **kwargs):
    example_row1 = 'ad_group_example,2019-01-01,0'
    example_row2 = 'ad_group_example,2019-01-01,4'
    return lambda x: [example_row1, example_row2]

def mock_video_query(*args, **kwargs):
    example_row1 = '1234567890\n'
    example_row2 = '1111111111\n'
    return lambda x: [example_row1, example_row2]

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
        "client_customer_ids": ["123-456-7890"],
        "report_name": "Custom Report",
        "report_type": "AD_PERFORMANCE_REPORT",
        "date_range_type": "LAST_7_DAYS",
        "start_date": "",
        "end_date": "",
        "download_format": "CSV",
        "fields": ("CampaignId", "Date", "Impressions"),
        "report_filter": {},
        "include_zero_impressions": True,
        "filter_on_video_campaigns": False,
        "include_client_customer_id": False,
    }

    def test_format_customer_id(self):
        assert GoogleAdsReader.format_customer_id(1234567890) == "123-456-7890"
        assert GoogleAdsReader.format_customer_id("abcdefjhij") is None
        assert GoogleAdsReader.format_customer_id(-1234567890) is None
        assert GoogleAdsReader.format_customer_id(None) is None
        assert GoogleAdsReader.format_customer_id(123456789) is None

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_add_report_filter(self):
        report_filter = {'field': "CampaignName", 'operator': 'IN', 'values': ['example']}
        report_definition = {'selector': {}}
        expected_output = {'selector': {'predicates': report_filter}}
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update({'report_filter': report_filter})
        GoogleAdsReader(**temp_kwargs).add_report_filter(report_definition)
        assert report_definition == expected_output

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_missing_field_report_filter(self):
        missing_field = {'wrong_key': "CampaignName", 'operator': 'IN', 'values': ['example']}
        report_definition = {'selector': {}}
        with self.assertRaises(ClickException):
            temp_kwargs = self.kwargs.copy()
            temp_kwargs.update({'report_filter': missing_field})
            GoogleAdsReader(**temp_kwargs).add_report_filter(report_definition)

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_invalid_report_filter(self):
        not_a_dict = ['field', 'operator', 'values']
        report_definition = {'selector': {}}
        with self.assertRaises(AttributeError):
            temp_kwargs = self.kwargs.copy()
            temp_kwargs.update({'report_filter': not_a_dict})
            GoogleAdsReader(**temp_kwargs).add_report_filter(report_definition)

    @mock.patch("nck.readers.googleads_reader.GoogleAdsReader.fetch_report_from_gads_client_customer_obj")
    @mock.patch("nck.readers.googleads_reader.codecs.getreader", side_effect=mock_query)
    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_read_data(self, mock_report, mock_query):
        reader = GoogleAdsReader(**self.kwargs)
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
            assert len(list(data.readlines())) != 0
            for record, output in zip(data.readlines(), iter(expected)):
                assert record == output

    @mock.patch("nck.readers.googleads_reader.GoogleAdsReader.fetch_report_from_gads_client_customer_obj")
    @mock.patch("nck.readers.googleads_reader.codecs.getreader", side_effect=mock_query)
    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_read_data_and_include_account_id(self, mock_report, mock_query):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update({'include_client_customer_id': True})
        reader = GoogleAdsReader(**temp_kwargs)

        expected = [
            {
                "AdGroupName": "ad_group_example",
                "AccountId": "123-456-7890",
                "Date": "2019-01-01",
                "Impressions": "0"},
            {
                "AdGroupName": "ad_group_example",
                "AccountId": "123-456-7890",
                "Date": "2019-01-01",
                "Impressions": "4"}
        ]

        for data in reader.read():
            assert len(list(data.readlines())) != 0
            for record, output in zip(data.readlines(), iter(expected)):
                assert record == output

    @mock.patch("nck.readers.googleads_reader.GoogleAdsReader.fetch_report_from_gads_client_customer_obj")
    @mock.patch("nck.readers.googleads_reader.codecs.getreader", side_effect=mock_video_query)
    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_list_video_campaign_ids(self, mock_report, mock_query):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update({"filter_on_video_campaigns": True})
        expected = set([
            '1234567890',
            '1111111111',
        ])
        set_ids = GoogleAdsReader(**temp_kwargs).list_video_campaign_ids()
        assert len(set_ids) != 0
        assert set_ids == expected

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_no_campaignid_for_video_report_definition(self):
        no_campaignid_field = {"fields": ("CampaignName", "Date", "Impressions")}
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update(no_campaignid_field)
        with self.assertRaises(ClickException):
            GoogleAdsReader(**temp_kwargs).get_video_campaign_report_definition()

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_get_video_report_definition_standard_date(self):
        video_report_def = GoogleAdsReader(**self.kwargs).get_video_campaign_report_definition()
        expected_output_standard_date = {
            "reportName": "video campaigns ids",
            "dateRangeType": "LAST_7_DAYS",
            "reportType": "VIDEO_PERFORMANCE_REPORT",
            "downloadFormat": "CSV",
            "selector": {"fields": "CampaignId"},
        }
        assert video_report_def == expected_output_standard_date

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_get_video_report_definition_custom_date(self):
        custom_date_param = {
            'date_range_type': "CUSTOM_DATE",
            'start_date': datetime.date(2019, 1, 1),
            'end_date': datetime.date(2019, 3, 1)
        }
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update(custom_date_param)
        video_report_def = GoogleAdsReader(**temp_kwargs).get_video_campaign_report_definition()
        expected_output_custom_date = {
            "reportName": "video campaigns ids",
            "dateRangeType": "CUSTOM_DATE",
            "reportType": "VIDEO_PERFORMANCE_REPORT",
            "downloadFormat": "CSV",
            "selector": {
                "fields": "CampaignId",
                "dateRange": {"min": "20190101", "max": "20190301"},
            },
        }
        assert video_report_def == expected_output_custom_date

    @parameterized.expand(['1231231234', '123_123_1234', 'abc-abc-abcd', '1234-123-123'])
    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_refuse_incorrect_id(self, invalid_input):
        """Test the function checking the Client Customer IDs
        format in order to refuse an invalid input
        """
        expected = None
        assert GoogleAdsReader(**self.kwargs).valid_client_customer_id(invalid_input) == expected

    @parameterized.expand(['123-123-1234'])
    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_validate_correct_id(self, valid_input):
        """Test the function checking the Client Customer IDs
        format in order to refuse an invalid input
        """
        cond = GoogleAdsReader(**self.kwargs).valid_client_customer_id(valid_input)
        assert cond

    @parameterized.expand([
        ["end_date", {'date_range_type': "CUSTOM_DATE", 'start_date': datetime.date(2019, 1, 1), 'end_date': None}],
        ["start_date", {'date_range_type': "CUSTOM_DATE", 'start_date': None, 'end_date': datetime.date(2019, 1, 1)}],
        ["all_dates", {'date_range_type': "CUSTOM_DATE", 'start_date': None, 'end_date': None}],
    ])
    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_add_invalid_custom_period_to_report_definition(self, name, invalid_parameter):
        """Test that report definition dateRangeType is replaced by default value
        when no start_date and end_date are provided
        """
        expected_range_type = DATE_RANGE_TYPE_POSSIBLE_VALUES[0]

        report_definition = self.get_report_definition(invalid_parameter['date_range_type'])

        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update(invalid_parameter)
        GoogleAdsReader(**temp_kwargs).add_period_to_report_definition(report_definition)

        assert report_definition['dateRangeType'] == expected_range_type
        with self.assertRaises(KeyError):
            report_definition['start_date']
            report_definition['end_date']

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_add_valid_custom_period_to_report_definition(self):
        """Test that report definition with custom dateRangeType is correctly implemented
        when start_date and end_date are provided
        """

        valid_parameter = {
            'date_range_type': "CUSTOM_DATE",
            'start_date': datetime.date(2019, 1, 1),
            'end_date': datetime.date(2021, 2, 1)
        }

        report_definition = self.get_report_definition(valid_parameter['date_range_type'])
        expected_date_range = {
            "min": valid_parameter['start_date'].strftime(DATEFORMAT),
            "max": valid_parameter['end_date'].strftime(DATEFORMAT)
        }

        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update(valid_parameter)
        GoogleAdsReader(**temp_kwargs).add_period_to_report_definition(report_definition)

        assert report_definition['dateRangeType'] == valid_parameter['date_range_type']
        assert report_definition['selector']['dateRange'] == expected_date_range

    @parameterized.expand([
        ["with_date", {'date_range_type': "LAST_7_DAYS", 'start_date': datetime.date(2019, 1, 1), 'end_date': None}],
        ["no_date", {'date_range_type': "LAST_30_DAYS", 'start_date': None, 'end_date': None}],
    ])
    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_add_standard_period_to_report_definition(self, name, valid_parameter):
        """Test that report definition with classic dateRangeType is correctly implemented
        whether or not the user specify a date range (not taken into account)
        """
        report_definition = self.get_report_definition(valid_parameter['date_range_type'])

        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update(valid_parameter)
        GoogleAdsReader(**temp_kwargs).add_period_to_report_definition(report_definition)

        assert report_definition['dateRangeType'] == valid_parameter['date_range_type']
        with self.assertRaises(KeyError):
            report_definition['start_date']
        with self.assertRaises(KeyError):
            report_definition['end_date']

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
