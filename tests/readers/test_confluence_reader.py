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

from unittest import TestCase, mock
from click import ClickException

from nck.readers.confluence_reader import ConfluenceReader

KEY1_RAW_RESPONSE_PAGE0 = {
    "results":
    [
        {
            "title": "Making API requests with NCK",
            "space": {"name": "How To Guides"},
            "metadata": {"labels": {"results": [{"name": "api"}]}}
        },
        {
            "title": "Writting a Client Case",
            "space": {"name": "How To Guides"},
            "metadata": {"labels": {"results": [{"name": "confluence"}]}}
        }
    ],
    "_links": {"next": "link_to_next_request_page"}
}

KEY1_RAW_RESPONSE_PAGE1 = {
    "results":
    [
        {
            "title": "Developping with Github",
            "space": {"name": "How To Guides"},
            "metadata": {"labels": {"results": [{"name": "git"}]}}
        }
    ],
    "_links": {}
}

KEY1_FINAL_RECORDS = [
    {"title": "Making API requests with NCK", "space.name": "How To Guides", "label_names": "api"},
    {"title": "Writting a Client Case", "space.name": "How To Guides", "label_names": "confluence"},
    {"title": "Developping with Github", "space.name": "How To Guides", "label_names": "git"}
]

KEY2_FINAL_RECORDS = [
    {"title": "Samsung - Precision Marketing", "space.name": "Clients", "label_names": "pm"},
    {"title": "P&G - Demand Sensing", "space.name": "Clients", "label_names": "ai"},
    {"title": "Orange - Call center automation", "space.name": "Clients", "label_names": "ai"},
]


class ConfluenceReaderTest(TestCase):

    kwargs = {
        "user_login": "firstname.name@your-domain.com",
        "api_token": "aAbBcCdDeE12fFgGhHiIjJ34",
        "atlassian_domain": "https://your-domain.com",
        "content_type": "page",
        "spacekey": [],
        "field": ["title", "space.name", "label_names"],
        "normalize_stream": False
    }

    @mock.patch(
        "nck.readers.confluence_reader.CUSTOM_FIELDS",
        {
            "custom_field_A": {"specific_to_spacekeys": ["KEY1"]},
            "custom_field_B": {"specific_to_spacekeys": ["KEY1", "KEY2"]},
            "custom_field_C": {}
        }
    )
    def test__validate_spacekeys(self):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update({"field": ["custom_field_A", "custom_field_B", "custom_field_C"]})
        with self.assertRaises(ClickException):
            ConfluenceReader(**temp_kwargs)

    def test__build_headers(self):
        output = ConfluenceReader(**self.kwargs).headers
        expected = {
            "Authorization": "Basic Zmlyc3RuYW1lLm5hbWVAeW91ci1kb21haW4uY29tOmFBYkJjQ2REZUUxMmZGZ0doSGlJakozNA==",
            "Content-Type": "application/json"
        }
        self.assertDictEqual(output, expected)

    def test__build_params(self):
        output = ConfluenceReader(**self.kwargs).build_params()
        expected = {"type": "page", "expand": "title,space.name,metadata.labels.results"}
        self.assertDictEqual(output, expected)

    @mock.patch.object(
        ConfluenceReader,
        "get_raw_response",
        side_effect=[KEY1_RAW_RESPONSE_PAGE0, KEY1_RAW_RESPONSE_PAGE1]
    )
    def test__get_report_generator(self, mock_get_raw_response):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update({"spacekey": ["KEY1"]})
        output = ConfluenceReader(**self.kwargs).get_report_generator()
        expected = iter(KEY1_FINAL_RECORDS)
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)

    @mock.patch.object(
        ConfluenceReader,
        "get_report_generator",
        side_effect=[iter(KEY1_FINAL_RECORDS), iter(KEY2_FINAL_RECORDS)]
    )
    def test__get_aggregated_report_generator(self, mock_get_report_generator):
        temp_kwargs = self.kwargs.copy()
        temp_kwargs.update({"spacekey": ["KEY1", "KEY2"]})
        output = ConfluenceReader(**self.kwargs).get_aggregated_report_generator()
        expected = iter(KEY1_FINAL_RECORDS + KEY2_FINAL_RECORDS)
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)
