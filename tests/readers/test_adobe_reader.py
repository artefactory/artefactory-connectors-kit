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
import datetime
from nck.readers.adobe_reader import AdobeReader
from unittest import TestCase, mock


class AdobeReaderTest(TestCase):
    DATEFORMAT = "%Y-%m-%d"

    @mock.patch("nck.readers.adobe_reader.AdobeReader.query_report")
    @mock.patch("nck.readers.adobe_reader.AdobeReader.download_report")
    def test_read(self, mock_download_report, mock_query_report):
        elt_ids = ["category", "geocountry"]
        mets_ids = [
            "cartadditions",
            "cartviews",
            "cartremovals",
            "participationunits",
            "participationrevenue",
            "visits",
            "pageviews",
            "event46",
            "event26",
            "event35",
        ]
        rsuid = "sssamsung4ae"
        kwargs = {
            "username": "",
            "password": "",
            "report_suite_id": rsuid,
            "date_granularity": "day",
            "report_element_id": elt_ids,
            "report_metric_id": mets_ids,
            "start_date": datetime.datetime(2019, 11, 15),
            "end_date": datetime.datetime(2019, 11, 20),
        }
        reader = AdobeReader(**kwargs)

        def test_read_empty_data(mock_download_report, mock_query_report):
            mock_download_report.return_value = [{"responseAgregationType": "byPage"}]
            mock_query_report.return_value = {"reportID": "0"}
            if len(list(reader.read())) > 1:
                assert False, "Data is not empty"

        test_read_empty_data(mock_download_report, mock_query_report)
