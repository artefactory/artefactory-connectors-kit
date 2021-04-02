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
import logging
from unittest import TestCase

from ack.utils.text import parse_decoded_line, get_report_generator_from_flat_file


class TestTextUtilsMethod(TestCase):
    def test_get_report_generator__multiple_encodings(self):
        test_string_to_encode = "2020-01-01,France,1234,10"
        lines = [
            b"Date,Country,AdvertiserId,Impressions",
            test_string_to_encode.encode("utf-8"),
            test_string_to_encode.encode("ascii"),
            test_string_to_encode.encode("windows-1252"),
            test_string_to_encode.encode("latin_1"),
        ]
        line_iterator = iter(lines)
        expected = {
            "Date": "2020-01-01",
            "Country": "France",
            "AdvertiserId": "1234",
            "Impressions": "10",
        }
        for output in get_report_generator_from_flat_file(line_iterator):
            self.assertDictEqual(output, expected)

    def test_get_report_generator__invalid_byte(self):
        lines = [
            b"Date,Country,AdvertiserId,Impressions",
            b'2020-01-01,"   \x91\xea\xd0$",1234,10',
        ]
        line_iterator = iter(lines)
        expected = {
            "Date": "2020-01-01",
            "Country": "   $",
            "AdvertiserId": "1234",
            "Impressions": "10",
        }
        with self.assertLogs(level=logging.INFO) as log:
            for output in get_report_generator_from_flat_file(line_iterator):
                self.assertDictEqual(output, expected)
        self.assertEqual(
            log.output,
            [
                "WARNING:root:An error has occurred while parsing the file."
                "The line could not be decoded in utf-8."
                "Invalid input that the codec failed on: b'\\x91'"
            ],
        )

    def test_get_report_generator__no_bytes(self):
        lines = ["Date,Country,AdvertiserId,Impressions", "2020-01-01,France,1234,10"]
        line_iterator = iter(lines)
        expected = {
            "Date": "2020-01-01",
            "Country": "France",
            "AdvertiserId": "1234",
            "Impressions": "10",
        }
        for output in get_report_generator_from_flat_file(line_iterator):
            self.assertDictEqual(output, expected)

    def test_parse_decoded_line(self):
        lines = [
            'abc, 1, 0.0, 4, "a,b,c", abc',
            '"abc", 1, 0.0, 4, "a,b,c", abc',
            "abc, 1, 0.0, 4, abc, abc",
        ]
        expected_lines = [
            ["abc", "1", "0.0", "4", "a,b,c", "abc"],
            ["abc", "1", "0.0", "4", "a,b,c", "abc"],
            ["abc", "1", "0.0", "4", "abc", "abc"],
        ]

        for line, expected_line in zip(lines, expected_lines):
            output_line = parse_decoded_line(line)
            self.assertEqual(output_line, expected_line)

    def test_get_report_generator__add_column(self):
        lines = [
            b"Date,AdvertiserId,Reach",
            b"2020-01-01,1234,1000",
            b"2020-01-01,5678,2000",
        ]
        expected = [
            {"Date": "2020-01-01", "AdvertiserId": "1234", "Reach": "1000", "Campaign": "XMas Sale", "Country": "France"},
            {"Date": "2020-01-01", "AdvertiserId": "5678", "Reach": "2000", "Campaign": "XMas Sale", "Country": "France"},
        ]
        line_iterator = iter(lines)
        output = get_report_generator_from_flat_file(
            line_iterator, add_column=True, column_dict={"Campaign": "XMas Sale", "Country": "France"},
        )
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)

    def test_get_report_generator__file_with_headers_only(self):
        lines = [b"Just,Headers,in,this,empty,report"]
        line_iterator = iter(lines)
        self.assertFalse(
            next(get_report_generator_from_flat_file(line_iterator), False), "Data is not empty",
        )

    def test_get_report_generator__skip_when_no_match_with_headers_length(self):
        lines = [
            b"Date,AdvertiserId,Impressions",
            b"2020-01-01,1234,10",
            b"2020-01-01,5678,20",
            b"Copyrigth: report downloaded from Artefact.com",
        ]
        line_iterator = iter(lines)
        output = get_report_generator_from_flat_file(line_iterator, skip_n_first=0, skip_n_last=0)
        expected = [
            {"Date": "2020-01-01", "AdvertiserId": "1234", "Impressions": "10"},
            {"Date": "2020-01-01", "AdvertiserId": "5678", "Impressions": "20"},
        ]
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)

    def test_get_report_generator__skip_blank(self):
        lines = [
            b"Date,AdvertiserId,Impressions",
            b"2020-01-01,1234,10",
            b"",
            b"2020-01-01,5678,20",
        ]
        line_iterator = iter(lines)
        output = get_report_generator_from_flat_file(line_iterator, skip_n_first=0, skip_n_last=0)
        expected = [
            {"Date": "2020-01-01", "AdvertiserId": "1234", "Impressions": "10"},
            {"Date": "2020-01-01", "AdvertiserId": "5678", "Impressions": "20"},
        ]
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)

    def test_get_report_generator__skip_first_and_last(self):
        lines = [
            b"(Not desired first line)",
            b"(Not desired second line)",
            b"Date,AdvertiserId,Impressions",
            b"2020-01-01,1234,10",
            b"2020-01-01,5678,20",
            b"(Not desired last line)",
        ]
        line_iterator = iter(lines)
        output = get_report_generator_from_flat_file(line_iterator, skip_n_first=2, skip_n_last=1)
        expected = [
            {"Date": "2020-01-01", "AdvertiserId": "1234", "Impressions": "10"},
            {"Date": "2020-01-01", "AdvertiserId": "5678", "Impressions": "20"},
        ]
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)

    def test_get_report_generator__skip_last_with_blank_at_end_of_file(self):
        lines = [
            b"Date,AdvertiserId,Impressions",
            b"2020-01-01,1234,10",
            b"2020-01-01,5678,20",
            b"(Not desired last line)",
            b"",
        ]
        line_iterator = iter(lines)
        output = get_report_generator_from_flat_file(line_iterator, skip_n_first=0, skip_n_last=1)
        expected = [
            {"Date": "2020-01-01", "AdvertiserId": "1234", "Impressions": "10"},
            {"Date": "2020-01-01", "AdvertiserId": "5678", "Impressions": "20"},
        ]
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)

    def test_get_report_generator__skip_no_first_nor_last(self):
        lines = [
            b"Date,AdvertiserId,Impressions",
            b"2020-01-01,1234,10",
            b"2020-01-01,5678,20",
        ]
        line_iterator = iter(lines)
        output = get_report_generator_from_flat_file(line_iterator, skip_n_first=0, skip_n_last=0)
        expected = [
            {"Date": "2020-01-01", "AdvertiserId": "1234", "Impressions": "10"},
            {"Date": "2020-01-01", "AdvertiserId": "5678", "Impressions": "20"},
        ]
        for output_record, expected_record in zip(output, expected):
            self.assertEqual(output_record, expected_record)
