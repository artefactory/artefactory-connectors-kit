from nck.readers.dv360_reader import DV360Reader
from unittest import TestCase, mock


class TestDV360Reader(TestCase):
    def mock_dv360_reader(self, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)

    @mock.patch.object(DV360Reader, "__init__", mock_dv360_reader)
    def test_get_sdf_body(self):
        kwargs = {}
        reader = DV360Reader(**kwargs)
        reader.kwargs = {
            "file_type": ["FILE_TYPE_INSERTION_ORDER", "FILE_TYPE_CAMPAIGN"],
            "filter_type": "FILTER_TYPE_ADVERTISER_ID",
            "advertiser_id": "4242424",
        }

        expected_query_body = {
            "parentEntityFilter": {
                "fileType": ["FILE_TYPE_INSERTION_ORDER", "FILE_TYPE_CAMPAIGN"],
                "filterType": "FILTER_TYPE_ADVERTISER_ID",
            },
            "version": "SDF_VERSION_5_2",
            "advertiserId": "4242424",
        }

        self.assertDictEqual(reader._DV360Reader__get_sdf_body(), expected_query_body)
