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
import unittest
import logging

from parameterized import parameterized

from nck.helpers.api_client_helper import (get_dict_with_keys_converted_to_new_string_format,
                                           to_pascal_key)


class ApiClientHelperTest(unittest.TestCase):

    def test_string_conversion_to_camel_case(self):
        self.assertDictEqual(
            get_dict_with_keys_converted_to_new_string_format(
                abc_de=1,
                abc="abc",
                abc_de_fg=2
            ),
            {
                "AbcDe": 1,
                "Abc": "abc",
                "AbcDeFg": 2
            }
        )

    @parameterized.expand([
        ("test", "Test"),
        ("test_test", "TestTest"),
        ("test_test_test", "TestTestTest"),
        ("tEST", "Test"),
        ("t_e_s_t", "TEST")
    ])
    def test_to_pascal_key(self, key, pascal_key):
        self.assertEqual(to_pascal_key(key), pascal_key)

    def test_unknown_case(self):
        with self.assertLogs() as cm:
            logging.getLogger("ApiClient")
            get_dict_with_keys_converted_to_new_string_format("UnknownCase")
            self.assertEqual(
                cm.output,
                ["ERROR:root:Unable to convert to new string format. Format not in ['PascalCase']"]
            )
