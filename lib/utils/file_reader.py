from enum import Enum
import csv
import codecs
import gzip
import json


def format_csv_delimiter(csv_delimiter):
    _csv_delimiter = csv_delimiter.encode().decode('unicode_escape')
    if csv_delimiter == 'newline':
        _csv_delimiter = '\n'
    if csv_delimiter == 'tab':
        _csv_delimiter = '\t'
    return _csv_delimiter


def format_csv_fieldnames(csv_fieldnames):
    if csv_fieldnames is None:
        _csv_fieldnames = csv_fieldnames
    elif isinstance(csv_fieldnames, list):
        _csv_fieldnames = csv_fieldnames
    elif isinstance(csv_fieldnames, (str, bytes)):
        _csv_fieldnames = json.loads(csv_fieldnames)
    else:
        raise TypeError(f'The CSV fieldnames is of the following type: {type(csv_fieldnames)}.')
    assert isinstance(_csv_fieldnames, list)
    return _csv_fieldnames


class CSVReader(object):
    def __init__(self, csv_delimiter, csv_fieldnames, **kwargs):
        self.csv_delimiter = format_csv_delimiter(csv_delimiter)
        self.csv_fieldnames = format_csv_fieldnames(csv_fieldnames)

        self.csv_reader = lambda fd: self.read_csv(fd, **kwargs)

    def read_csv(self, fd, **kwargs):
        fd.seek(0)
        fd = self.decompress(fd)
        return csv.DictReader(codecs.iterdecode(fd, encoding='utf-8'), delimiter=str(self.csv_delimiter),
                              fieldnames=self.csv_fieldnames, **kwargs)

    def decompress(self, fd):
        return fd

    def get_csv_reader(self):
        return self.csv_reader


class GZReader(CSVReader):
    def decompress(self, fd):
        gzf = gzip.GzipFile(mode='rb', fileobj=fd)
        return gzf


class FileEnum(Enum):
    CSV = CSVReader
    GZ = GZReader
