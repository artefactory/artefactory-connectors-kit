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
from enum import Enum
import csv
import codecs
import gzip
import zipfile
import json

csv.field_size_limit(1000000)


def unzip(input_file, output_path):
    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        zip_ref.extractall(output_path)


def sdf_to_njson_generator(path_to_file):
    csv_reader = CSVReader(csv_delimiter=",", csv_fieldnames=None)
    with open(path_to_file, "rb") as fd:
        dict_reader = csv_reader.read_csv(fd)
        for line in dict_reader:
            yield line


def format_csv_delimiter(csv_delimiter):
    _csv_delimiter = csv_delimiter.encode().decode("unicode_escape")
    if csv_delimiter == "newline":
        _csv_delimiter = "\n"
    if csv_delimiter == "tab":
        _csv_delimiter = "\t"
    return _csv_delimiter


def format_csv_fieldnames(csv_fieldnames):
    if isinstance(csv_fieldnames, list):
        _csv_fieldnames = csv_fieldnames
    elif isinstance(csv_fieldnames, (str, bytes)):
        _csv_fieldnames = json.loads(csv_fieldnames)
    else:
        raise TypeError(
            f"The CSV fieldnames is of the following type: {type(csv_fieldnames)}."
        )
    assert isinstance(_csv_fieldnames, list)
    return _csv_fieldnames


class CSVReader(object):
    def __init__(self, csv_delimiter, csv_fieldnames, **kwargs):
        self.csv_delimiter = format_csv_delimiter(csv_delimiter)
        self.csv_fieldnames = format_csv_fieldnames(csv_fieldnames) if csv_fieldnames is not None else None
        self.csv_reader = lambda fd: self.read_csv(fd, **kwargs)

    def read_csv(self, fd, **kwargs):
        fd.seek(0)
        fd = self.decompress(fd)
        return csv.DictReader(
            codecs.iterdecode(fd, encoding="utf-8"),
            delimiter=str(self.csv_delimiter),
            fieldnames=self.csv_fieldnames,
            **kwargs,
        )

    def decompress(self, fd):
        return fd

    def get_csv_reader(self):
        return self.csv_reader


class GZReader(CSVReader):
    def decompress(self, fd):
        gzf = gzip.GzipFile(mode="rb", fileobj=fd)
        return gzf


class FileEnum(Enum):
    CSV = CSVReader
    GZ = GZReader
