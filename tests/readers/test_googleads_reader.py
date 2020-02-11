from unittest import TestCase, mock

from nck.readers.googleads_reader import GoogleAdsReader
from nck.helpers.googleads_helper import REPORT_TYPE_POSSIBLE_VALUES, DATE_RANGE_TYPE_POSSIBLE_VALUES, ENCODING

from googleads import adwords


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
        "client_customer_ids": "",
        "report_type": "AD_PERFORMANCE_REPORT",
        "fields": ("AdGroupName","Date", "Impressions"),
    }

    @mock.patch.object(GoogleAdsReader, "__init__", mock_googleads_reader)
    def test_format_customer_id(self):
        unformatted_customer_id = repr(1234567890)
        expected = "123-456-7890"
        assert GoogleAdsReader(**self.kwargs).format_customer_id(unformatted_customer_id) == expected
