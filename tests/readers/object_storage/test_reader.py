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

import csv
import io
import json
from unittest import TestCase, mock

from ack.readers.object_storage.reader import ObjectStorageReader
from parameterized import parameterized

mock_csv_names = ["a.csv", "a.njson", "b.csv", "b.njson"]
mock_csv_files = [
    [["a", "b", "c"], [4, 5, 6], [7, 8, 9]],
    [{"a": "4", "b": "5", "c": "6"}, {"a": "7", "b": "8", "c": "9"}],
    [["a", "b", "c"], [4, 5, 6], [7, 8, 9]],
    [{"a": "4", "b": "5", "c": "6"}, {"a": "7", "b": "8", "c": "9"}],
]

mock_timestamp = [
    1614179262,
    1614179272,
    1614179277,
    16141792778,
]


def mock_to_object(self, _object):
    return _object


def mock_list_objects(self, bucket, prefix):
    a = list(zip(mock_csv_names, mock_timestamp, mock_csv_files))
    return [x for x in a if x[0].startswith(prefix)]


def mock_get_timestamp(self, _object, **kwargs):
    return _object[1]


def write_to_file(self, _object, f, **kwargs):

    if self._format == "csv":

        text_file = io.TextIOWrapper(f, encoding="utf-8", newline="")
        w = csv.writer(text_file)
        w.writerows(_object[2])
        text_file.detach()

    else:

        text_file = io.TextIOWrapper(f, encoding="utf-8")
        for line in _object[2]:

            json.dump(line, text_file)
            text_file.write("\n")
        text_file.detach()


def mock_get_key(self, _object, **kwargs):
    return _object[0]


@mock.patch("ack.readers.object_storage.reader.ObjectStorageReader.create_client")
@mock.patch("ack.readers.object_storage.reader.ObjectStorageReader.create_bucket")
@mock.patch.object(ObjectStorageReader, "download_object_to_file", write_to_file)
@mock.patch.object(ObjectStorageReader, "to_object", mock_to_object)
@mock.patch.object(ObjectStorageReader, "get_timestamp", mock_get_timestamp)
@mock.patch.object(ObjectStorageReader, "list_objects", mock_list_objects)
@mock.patch.object(ObjectStorageReader, "get_key", mock_get_key)
class ObjectStorageReaderTest(TestCase):
    def test_wrong_format(self, a, b):
        with self.assertRaises(NotImplementedError):
            ObjectStorageReader(
                bucket="", prefix=["a"], file_format="txt", dest_key_split=-1, csv_delimiter=",", csv_fieldnames=None
            )

    @parameterized.expand([("njson", 2), ("csv", 2)])
    def test_ObjectStorageReader_filter_files(self, a, b, format, nb_files_expected):
        reader = ObjectStorageReader(
            bucket="", prefix=[""], file_format=format, dest_key_split=-1, csv_delimiter=",", csv_fieldnames=None
        )
        nb_file = len(list(reader.read()))
        self.assertEqual(nb_file, nb_files_expected)

    @parameterized.expand(
        [
            ("njson", [{"a": "4", "b": "5", "c": "6"}, {"a": "7", "b": "8", "c": "9"}]),
            ("csv", [{"a": "4", "b": "5", "c": "6"}, {"a": "7", "b": "8", "c": "9"}]),
        ]
    )
    def test_ObjectStorageReader_read_all_file(self, a, b, format, expected):
        reader = ObjectStorageReader(
            bucket="", prefix=["a"], file_format="csv", dest_key_split=-1, csv_delimiter=",", csv_fieldnames=None
        )
        for file in reader.read():
            for expect, data in zip(expected, file.readlines()):
                self.assertEqual(expect, data)
