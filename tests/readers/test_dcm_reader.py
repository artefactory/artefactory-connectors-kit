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

from nck.readers.dcm_reader import DcmReader

logger = logging.getLogger("DCM_reader_test")


class DCMReaderTest(TestCase):
    def mock_dcm_reader(self, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)

    kwargs = {"metrics": ["impressions", "clicks"], "dimensions": ["date"]}

    @mock.patch.object(DcmReader, "__init__", mock_dcm_reader)
    def test_empty_data(self):
        reader = DcmReader(**self.kwargs)
        input_report = (row for row in [b"No", b"Consistent", b"Data"])
        if len(list(reader.format_response(input_report))) > 0:
            assert False, "Data is not empty"

    @mock.patch.object(DcmReader, "__init__", mock_dcm_reader)
    def test_format_data(self):
        reader = DcmReader(**self.kwargs)
        input_report = (row for row in [b"x", b"x", b"Report Fields", b"headers", b"1,2,3", b"4,5,6", b"Grand Total"])
        expected = [{"date": "1", "impressions": "2", "clicks": "3"}, {"date": "4", "impressions": "5", "clicks": "6"}]
        input_list = list(reader.format_response(input_report))
        assert len(input_list) == len(expected)

        logger.info(f"{str(input_list)}\n{str(expected)}")
        for input_row, output in zip(input_list, expected):
            assert input_row == output
