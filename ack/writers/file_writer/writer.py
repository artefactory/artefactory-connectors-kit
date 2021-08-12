from ack.writers.formatters.formatter import Formatter
from ack.writers.writer import Writer


class FileWriter(Writer):
    def __init__(self, file_format):
        self._file_format = file_format
        self.formatter = Formatter(file_format)
        self.formatter.open("test")

    def write(self, stream):
        raise NotImplementedError
