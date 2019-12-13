from datetime import datetime
from lib.readers.adobe_reader import AdobeReader
from unittest import TestCase, mock


class AdobeReaderTest(TestCase):
    DATEFORMAT = "%Y-%m-%d"

    @mock.patch("lib.readers.AdobeReader.download_report")
    def test_read(self, mock_download_report):
        elt_ids = ['category','geocountry']
        mets_ids = ['cartadditions', 'cartviews','cartremovals', 'participationunits', 'participationrevenue', 'visits', 'pageviews','event46','event26','event35']
        rsuid = 'sssamsung4ae'
        kwargs = {
            "username": "",
            "password": "",
            "report_suite_id":rsuid,
            "date_granularity":"day",
            "report_element_id":elt_ids,
            "report_metric_id":mets_ids,
            "date_start":datetime.datetime(2019, 11,15),
            "date_stop":datetime.datetime(2019, 11,20)
        }
        reader = AdobeReader(**kwargs)

        def test_read_empty_data(mmock_download_report):
            mock_download_report.return_value = [{"responseAgregationType": "byPage"}]
            if len(list(reader.read())) > 1:
                assert False, "Data is not empty"
                
        test_read_empty_data(mock_download_report)
      