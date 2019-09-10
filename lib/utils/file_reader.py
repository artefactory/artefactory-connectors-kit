from enum import Enum
import csv
import codecs
import gzip


class FileReader(Enum):
    csv = 'csv'
    gz = 'gz'


class CSVReader(object):
    TAG = FileReader('csv')

    def __init__(self, csv_delimiter, csv_fieldnames, **kwargs):
        self.csv_delimiter = csv_delimiter.encode().decode('unicode_escape')
        if csv_delimiter == 'newline':
            self.csv_delimiter = '\n'

        if csv_fieldnames is None:
            self.csv_fieldnames = csv_fieldnames
        elif isinstance(csv_fieldnames, list):
            self.csv_fieldnames = csv_fieldnames
        elif isinstance(csv_fieldnames, str) or isinstance(csv_fieldnames, bytes):
            self.csv_fieldnames = eval(csv_fieldnames)
        else:
            raise TypeError("The CSV fieldnames is of the following type: %s." % type(csv_fieldnames))

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


class GZIPReader(CSVReader):
    TAG = FileReader('gz')

    def __init__(self, csv_delimiter, csv_fieldnames, **kwargs):
        super(GZIPReader, self).__init__(csv_delimiter, csv_fieldnames, **kwargs)

    def decompress(self, fd):
        gzf = gzip.GzipFile(mode='rb', fileobj=fd)
        return gzf
