import io
import json

import zstandard

from ack.utils.iterstream import IterStream


class Formatter(object):
    file_format = None
    content_type = None

    def __new__(cls, file_format):
        subclass_map = {subclass.file_format: subclass for subclass in cls.__subclasses__()}
        subclass = subclass_map[file_format]
        formatter = super(Formatter, subclass).__new__(subclass)
        return formatter

    def open_file(self, file, mode="wb"):
        raise NotImplementedError

    def format_stream_for_upload(self, stream):
        raise NotImplementedError


class NJsonFormatter(Formatter):
    file_format = "njson"
    content_type = "application/json"

    def open_file(self, path, mode="wb"):
        return open(path, mode)

    def format_stream_for_upload(self, stream):
        return stream.as_file()


class ZStandardFormatter(Formatter):
    file_format = "zstd"
    content_type = "application/zstd"
    zstd_context_compressor = zstandard.ZstdCompressor()

    def open_file(self, file, mode="wb"):
        return zstandard.open(file, mode)

    def encode_record_as_bytes(self, record):
        data = (json.dumps(record) + '\n').encode("utf-8")
        return self.zstd_context_compressor.compress(data)

    def format_stream_for_upload(self, stream):
        return io.BufferedReader(IterStream(self.encode_record_as_bytes, iter(stream)), buffer_size=io.DEFAULT_BUFFER_SIZE)
