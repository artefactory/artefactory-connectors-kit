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

from ack.readers.google_dv360.reader import GoogleDV360Reader
from unittest import TestCase, mock


class TestGoogleDV360Reader(TestCase):
    def mock_dv360_reader(self, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)

    @mock.patch.object(GoogleDV360Reader, "__init__", mock_dv360_reader)
    def test_get_sdf_body(self):
        kwargs = {}
        reader = GoogleDV360Reader(**kwargs)
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

        self.assertDictEqual(reader._GoogleDV360Reader__get_sdf_body(), expected_query_body)
