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
from datetime import date
from unittest.mock import patch

from parameterized import parameterized

from nck.utils.text import get_generator_dict_from_str_csv, get_generator_dict_from_str_tsv, parse_decoded_line


class TestTextUtilsMethod(TestCase):
    def test_multiple_encodings(self):
        test_string_to_encode = (
            "BR,test_partner,123,Active,test_advertiser,123,"
            "0,,test_io,123,Active,,test_line_item"
            ',123,0,,"",0.00,41'
        )
        lines = [
            (
                b"Country,Partner,Partner ID,Partner Status,Advertiser,Advertiser"
                b" ID,Advertiser Status,Advertiser Integration Code,Insertion"
                b" Order,Insertion Order ID,Insertion Order Status,Insertion"
                b" Order Integration Code,Line Item,Line Item ID,Line Item"
                b" Status,Line Item Integration Code,Targeted Data Providers,"
                b"Cookie Reach: Average Impression Frequency,Cookie Reach: "
                b"Impression Reach"
            ),
            test_string_to_encode.encode("utf-8"),
            test_string_to_encode.encode("ascii"),
            test_string_to_encode.encode("windows-1252"),
            test_string_to_encode.encode("latin_1"),
        ]
        line_iterator_multiple_encodings = (line for line in lines)
        expected_dict = {
            "Country": "BR",
            "Partner": "test_partner",
            "Partner ID": "123",
            "Partner Status": "Active",
            "Advertiser": "test_advertiser",
            "Advertiser ID": "123",
            "Advertiser Status": "0",
            "Advertiser Integration Code": "",
            "Insertion Order": "test_io",
            "Insertion Order ID": "123",
            "Insertion Order Status": "Active",
            "Insertion Order Integration Code": "",
            "Line Item": "test_line_item",
            "Line Item ID": "123",
            "Line Item Status": "0",
            "Line Item Integration Code": "",
            "Targeted Data Providers": "",
            "Cookie Reach: Average Impression Frequency": "0.00",
            "Cookie Reach: Impression Reach": "41",
        }
        for yielded_dict in get_generator_dict_from_str_csv(line_iterator_multiple_encodings):
            self.assertDictEqual(yielded_dict, expected_dict)

    def test_blank_line(self):
        lines = [
            (
                b"Country,Partner,Partner ID,Partner Status,Advertiser,Advertiser"
                b" ID,Advertiser Status,Advertiser Integration Code,Insertion"
                b" Order,Insertion Order ID,Insertion Order Status,Insertion"
                b" Order Integration Code,Line Item,Line Item ID,Line Item"
                b" Status,Line Item Integration Code,Targeted Data Providers,"
                b"Cookie Reach: Average Impression Frequency,Cookie Reach: "
                b"Impression Reach"
            ),
            b"(Not desired) Total line: ,,,,,,,,,,100,,100,100,,,,,,,100",
            "",
        ]
        line_iterator_with_blank_line = (line for line in lines)
        self.assertTrue(get_generator_dict_from_str_csv(line_iterator_with_blank_line))

        lines.insert(
            1,
            (
                b"BR,test_partner,123,Active,test_advertiser,123,"
                b"0,,test_io,123,Active,,test_line_item"
                b',123,0,,"",0.00,41'
            ),
        )
        expected_dict = {
            "Country": "BR",
            "Partner": "test_partner",
            "Partner ID": "123",
            "Partner Status": "Active",
            "Advertiser": "test_advertiser",
            "Advertiser ID": "123",
            "Advertiser Status": "0",
            "Advertiser Integration Code": "",
            "Insertion Order": "test_io",
            "Insertion Order ID": "123",
            "Insertion Order Status": "Active",
            "Insertion Order Integration Code": "",
            "Line Item": "test_line_item",
            "Line Item ID": "123",
            "Line Item Status": "0",
            "Line Item Integration Code": "",
            "Targeted Data Providers": "",
            "Cookie Reach: Average Impression Frequency": "0.00",
            "Cookie Reach: Impression Reach": "41",
        }
        line_iterator_with_blank_line = (line for line in lines)
        for dic in get_generator_dict_from_str_csv(line_iterator_with_blank_line):
            self.assertDictEqual(dic, expected_dict)

        lines.append("This is something that should not be here.")
        line_iterator_with_blank_line = (line for line in lines)
        test_result = get_generator_dict_from_str_csv(line_iterator_with_blank_line)
        self.assertEqual(len(list(test_result)), 1)
        for dic in test_result:
            self.assertEqual(dic, expected_dict)

    def test_invalid_byte(self):
        lines = [
            (
                b"Country,Partner,Partner ID,Partner Status,Advertiser,Advertiser"
                b" ID,Advertiser Status,Advertiser Integration Code,Insertion"
                b" Order,Insertion Order ID,Insertion Order Status,Insertion"
                b" Order Integration Code,Line Item,Line Item ID,Line Item"
                b" Status,Line Item Integration Code,Targeted Data Providers,"
                b"Cookie Reach: Average Impression Frequency,Cookie Reach: "
                b"Impression Reach"
            ),
            (
                b"BR,test_partner,123,Active,test_advertiser,123,"
                b"0,,test_io,123,Active,,test_line_item"
                b',123,0,,"   \x91\xea\xd0$",0.00,41'
            ),
        ]
        line_iterator_invalid_byte = (line for line in lines)
        expected_dict = {
            "Country": "BR",
            "Partner": "test_partner",
            "Partner ID": "123",
            "Partner Status": "Active",
            "Advertiser": "test_advertiser",
            "Advertiser ID": "123",
            "Advertiser Status": "0",
            "Advertiser Integration Code": "",
            "Insertion Order": "test_io",
            "Insertion Order ID": "123",
            "Insertion Order Status": "Active",
            "Insertion Order Integration Code": "",
            "Line Item": "test_line_item",
            "Line Item ID": "123",
            "Line Item Status": "0",
            "Line Item Integration Code": "",
            "Targeted Data Providers": "   $",
            "Cookie Reach: Average Impression Frequency": "0.00",
            "Cookie Reach: Impression Reach": "41",
        }
        with self.assertLogs(level=logging.INFO) as cm:
            for yielded_dict in get_generator_dict_from_str_csv(line_iterator_invalid_byte):
                self.assertDictEqual(yielded_dict, expected_dict)
        self.assertEqual(
            cm.output,
            [
                "WARNING:root:An error has occurred while parsing the file. "
                "The line could not be decoded in utf-8."
                "Invalid input that the codec failed on: b'\\x91'"
            ],
        )

    def test_response_not_binary(self):
        lines = [
            (
                "Country,Partner,Partner ID,Partner Status,Advertiser,Advertiser"
                " ID,Advertiser Status,Advertiser Integration Code,Insertion"
                " Order,Insertion Order ID,Insertion Order Status,Insertion"
                " Order Integration Code,Line Item,Line Item ID,Line Item"
                " Status,Line Item Integration Code,Targeted Data Providers,"
                "Cookie Reach: Average Impression Frequency,Cookie Reach: "
                "Impression Reach"
            ),
            (
                "BR,test_partner,123,Active,test_advertiser,123,"
                "0,,test_io,123,Active,,test_line_item"
                ',123,0,,"",0.00,41'
            ),
        ]
        expected_dict = {
            "Country": "BR",
            "Partner": "test_partner",
            "Partner ID": "123",
            "Partner Status": "Active",
            "Advertiser": "test_advertiser",
            "Advertiser ID": "123",
            "Advertiser Status": "0",
            "Advertiser Integration Code": "",
            "Insertion Order": "test_io",
            "Insertion Order ID": "123",
            "Insertion Order Status": "Active",
            "Insertion Order Integration Code": "",
            "Line Item": "test_line_item",
            "Line Item ID": "123",
            "Line Item Status": "0",
            "Line Item Integration Code": "",
            "Targeted Data Providers": "",
            "Cookie Reach: Average Impression Frequency": "0.00",
            "Cookie Reach: Impression Reach": "41",
        }
        line_iterator_with_blank_line = (line for line in lines)
        for dic in get_generator_dict_from_str_csv(line_iterator_with_blank_line):
            self.assertEqual(dic, expected_dict)

    def test_line_parsing(self):
        input_lines = ['abc, 1, 0.0, 4, "a,b,c", abc', '"abc", 1, 0.0, 4, "a,b,c", abc', "abc, 1, 0.0, 4, abc, abc"]
        expected_outputs = [
            ["abc", "1", "0.0", "4", "a,b,c", "abc"],
            ["abc", "1", "0.0", "4", "a,b,c", "abc"],
            ["abc", "1", "0.0", "4", "abc", "abc"],
        ]
        for index in range(len(input_lines)):
            self.assertEqual(parse_decoded_line(input_lines[index]), expected_outputs[index])

    def test_response_not_binary_with_date(self):
        lines = [
            (
                "Country,Partner,Partner ID,Partner Status,Advertiser,Advertiser"
                " ID,Advertiser Status,Advertiser Integration Code,Insertion"
                " Order,Insertion Order ID,Insertion Order Status,Insertion"
                " Order Integration Code,Line Item,Line Item ID,Line Item"
                " Status,Line Item Integration Code,Targeted Data Providers,"
                "Cookie Reach: Average Impression Frequency,Cookie Reach: "
                "Impression Reach"
            ),
            (
                "BR,test_partner,123,Active,test_advertiser,123,"
                "0,,test_io,123,Active,,test_line_item"
                ',123,0,,"",0.00,41'
            ),
        ]
        expected_dict = {
            "Country": "BR",
            "Partner": "test_partner",
            "Partner ID": "123",
            "Partner Status": "Active",
            "Advertiser": "test_advertiser",
            "Advertiser ID": "123",
            "Advertiser Status": "0",
            "Advertiser Integration Code": "",
            "Insertion Order": "test_io",
            "Insertion Order ID": "123",
            "Insertion Order Status": "Active",
            "Insertion Order Integration Code": "",
            "Line Item": "test_line_item",
            "Line Item ID": "123",
            "Line Item Status": "0",
            "Line Item Integration Code": "",
            "Targeted Data Providers": "",
            "Cookie Reach: Average Impression Frequency": "0.00",
            "Cookie Reach: Impression Reach": "41",
            "date_start": "2020/01/01",
            "date_stop": "2020/01/31",
        }
        line_iterator_with_blank_line = (line for line in lines)
        with patch("nck.utils.date_handler.date") as mock_date:
            mock_date.today.return_value = date(2020, 2, 1)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            for dic in get_generator_dict_from_str_csv(
                line_iterator_with_blank_line, add_date=True, day_range="PREVIOUS_MONTH", date_format="%Y/%m/%d"
            ):
                self.assertEqual(dic, expected_dict)

    def test_csv_with_headers_only(self):
        input_report = (row for row in [b"Just,Headers,in,this,empty,report"])
        self.assertFalse(next(get_generator_dict_from_str_csv(input_report), False), "Data is not empty")

    @parameterized.expand(
        [
            (
                True,
                [
                    b'"Perf report (2017-03-01 - 2020-03-25)"',
                    b"AdFormat\tAdGroupId\tAdGroupName",
                    b"IMAGE\t123\tAdGroup",
                    b"IMAGE\t123\tAdGroup",
                ],
            ),
            (False, [b"AdFormat\tAdGroupId\tAdGroupName", b"IMAGE\t123\tAdGroup", b"IMAGE\t123\tAdGroup"]),
        ]
    )
    def test_parse_tsv_with_first_row_skipped(self, skip_first_row, lines):
        expected_dict = {"AdFormat": "IMAGE", "AdGroupId": "123", "AdGroupName": "AdGroup"}
        line_iterator = (line for line in lines)
        for dic in get_generator_dict_from_str_tsv(line_iterator, skip_first_row=skip_first_row):
            self.assertEqual(dic, expected_dict)
