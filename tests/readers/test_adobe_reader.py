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

    elt_ids = ["trackingcode", "channel"]
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
    kwargs = {
        "client_id": "",
        "client_secret": "",
        "tech_account_id": "",
        "org_id": "",
        "private_key": "",
        "global_company_id": "",
        "report_suite_id": "XXXXX",
        "date_granularity": "day",
        "report_element_id": elt_ids,
        "report_metric_id": mets_ids,
        "start_date": datetime.datetime(2020, 1, 1),
        "end_date": datetime.datetime(2020, 1, 3),
    }

    @mock.patch("nck.clients.adobe_client.AdobeClient.__init__", return_value=None)
    @mock.patch(
        "nck.readers.adobe_reader.AdobeReader.query_report",
        return_value={"reportID": "XXXXX"},
    )
    @mock.patch(
        "nck.readers.adobe_reader.AdobeReader.download_report", return_value=None
    )
    def test_read_empty_data(
        self, mock_adobe_client, mock_query_report, mock_download_report
    ):
        reader = AdobeReader(**self.kwargs)
        self.assertFalse(len(list(reader.read())) > 1)
