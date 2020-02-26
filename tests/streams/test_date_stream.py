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
from nck.streams.format_date_stream import FormatDateStream
import json


class TestStreamBaseClassMethods(unittest.TestCase):
    data = """{"Date": "2020/01/27", "Impressions": "1286059"}
        {"Date": "2020/01/28", "Impressions": "889821"}
        {"Date": "2020/01/29", "Impressions": "1014673"}
        {"Date": "2020/01/30", "Impressions": "2119963"}
        {"Date": "2020/01/31", "Impressions": "1964449"}"""

    @staticmethod
    def data_generator(data):
        for elem in data.split('\n'):
            yield json.loads(elem)

    def test_usage(self):
        stream = FormatDateStream("result", self.data_generator(self.data), ["Date"])

        file = stream.as_file()
        buffer = "buf"
        res = b""
        while len(buffer) > 0:
            buffer = file.read(1024)
            res += buffer
        output = """{"Date": "2020-01-27", "Impressions": "1286059"}
                {"Date": "2020-01-28", "Impressions": "889821"}
                {"Date": "2020-01-29", "Impressions": "1014673"}
                {"Date": "2020-01-30", "Impressions": "2119963"}
                {"Date": "2020-01-31", "Impressions": "1964449"}
                """

        self.assertMultiLineEqual(res.decode().replace(" ", ""), output.replace(" ", ""))
