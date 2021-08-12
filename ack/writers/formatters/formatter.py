class Formatter(object):
    file_format = None

    def __new__(cls, file_format):
        subclass_map = {subclass.file_format: subclass for subclass in cls.__subclasses__()}
        subclass = subclass_map[file_format]
        instance = super(Formatter, subclass).__new__(subclass)
        return instance

    def open(self, file, mode="wb"):
        raise NotImplementedError


class NJsonFormatter(Formatter):
    file_format = "njson"

    def open(self, file, mode="wb"):
        print(f'{file} from NJsonFormatter')


class ZStandardFormatter(Formatter):
    file_format = "zstd"

    def open(self, file, mode="wb"):
        print(f'{file} from ZStandardFormatter')
