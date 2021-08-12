import zstandard


class Formatter(object):
    file_format = None

    def __new__(cls, file_format):
        subclass_map = {subclass.file_format: subclass for subclass in cls.__subclasses__()}
        subclass = subclass_map[file_format]
        formatter = super(Formatter, subclass).__new__(subclass)
        return formatter

    def open_file(self, file, mode="wb"):
        raise NotImplementedError


class NJsonFormatter(Formatter):
    file_format = "njson"

    def open_file(self, path, mode="wb"):
        return open(path, mode)


class ZStandardFormatter(Formatter):
    file_format = "zstd"

    def open_file(self, file, mode="wb"):
        return zstandard.open(file, mode)
