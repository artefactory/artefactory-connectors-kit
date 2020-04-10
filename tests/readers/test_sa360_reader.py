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
import logging

from nck.readers.sa360_reader import SA360Reader

logger = logging.getLogger("SA360_reader_test")


class SA360ReaderTest(TestCase):
    def mock_sa360_reader(self, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)

    kwargs = {"all_columns": ["impressions", "clicks"]}

    @mock.patch.object(SA360Reader, "__init__", mock_sa360_reader)
    def test_empty_data(self):
        reader = SA360Reader(**self.kwargs)
        input_report = (row for row in [b"Just Headers in this empty report"])
        self.assertFalse(next(reader.format_response(input_report), False), "Data is not empty")

    @mock.patch.object(SA360Reader, "__init__", mock_sa360_reader)
    def test_format_data(self):
        reader = SA360Reader(**self.kwargs)
        input_report = (row for row in [b"impressions,clicks", b"1,2", b"3,4"])
        expected = [{"impressions": "1", "clicks": "2"}, {"impressions": "3", "clicks": "4"}]
        input_list = list(reader.format_response(input_report))
        self.assertListEqual(input_list, expected)
