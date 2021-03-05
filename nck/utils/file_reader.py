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
import codecs
import gzip
import zipfile
import json

csv.field_size_limit(1000000)


def unzip(input_file, output_path):
    with zipfile.ZipFile(input_file, "r") as zip_ref:
        zip_ref.extractall(output_path)


def sdf_to_njson_generator(path_to_file):
    csv_reader = CSVReader(csv_delimiter=",", csv_fieldnames=None)
    with open(path_to_file, "rb") as fd:
        dict_reader = csv_reader.read(fd)
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
        raise TypeError(f"The CSV fieldnames is of the following type: {type(csv_fieldnames)}.")
    assert isinstance(_csv_fieldnames, list)
    return _csv_fieldnames


def create_file_reader(_format, **kwargs):
    if _format == "csv":
        return CSVReader(**kwargs)
    if _format == "gz":
        return GZReader(**kwargs)
    if _format == "njson":
        return NJSONReader(**kwargs)
    else:
        raise NotImplementedError(f"The file format {str(_format)} has not been implemented for reading yet.")


class FileReader:
    def __init__(self, **kwargs):
        self.reader = lambda fd: self.read(fd, **kwargs)

    def read(self, fd, **kwargs):
        fd.seek(0)
        return codecs.iterdecode(fd, encoding="utf8")

    def get_reader(self):
        return self.reader


class CSVReader(FileReader):
    def __init__(self, csv_delimiter, csv_fieldnames, **kwargs):
        self.csv_delimiter = format_csv_delimiter(csv_delimiter)
        self.csv_fieldnames = format_csv_fieldnames(csv_fieldnames) if csv_fieldnames is not None else None
        super().__init__(**kwargs)

    def read(self, fd, **kwargs):
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


class GZReader(CSVReader):
    def decompress(self, fd):
        gzf = gzip.GzipFile(mode="rb", fileobj=fd)
        return gzf


class NJSONReader(FileReader):
    def read(self, fd, **kwargs):
        fd.seek(0)
        return self.jsongene(fd, **kwargs)

    def jsongene(self, fd, **kwargs):
        for line in codecs.iterdecode(fd, encoding="utf8"):
            yield json.loads(line)
