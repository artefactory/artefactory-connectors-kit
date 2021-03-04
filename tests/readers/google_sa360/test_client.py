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
from unittest import TestCase
from nck.readers.google_sa360.client import SA360Client


class SA360ClientTest(TestCase):
    def test_generate_all_columns(self):
        standard = ["clicks", "impressions"]
        saved = ["savedColumn"]
        expected = [{"columnName": "clicks"}, {"columnName": "impressions"}, {"savedColumnName": "savedColumn"}]
        self.assertEqual(SA360Client.generate_columns(standard, saved), expected)
