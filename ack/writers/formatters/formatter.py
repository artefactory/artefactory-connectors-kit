import io
import json

import zstandard


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

    def open_file(self, file, mode="wb"):
        return zstandard.open(file, mode)

    def format_stream_for_upload(self, stream):
        class IterStream(io.RawIOBase):
            def __init__(self):
                self.leftover = None
                self.count = 0
                self.zstd_context_compressor = zstandard.ZstdCompressor()

            def readable(self):
                return True

            def readinto(self, b):
                try:
                    chunk_length = len(b)  # We're supposed to return at most this much
                    data = next(iter(stream))
                    encoded_data = (json.dumps(data) + '\n').encode('utf-8')
                    chunk = self.leftover or self.zstd_context_compressor.compress(encoded_data)
                    output, self.leftover = chunk[:chunk_length], chunk[chunk_length:]
                    b[: len(output)] = output
                    self.count += len(output)
                    return len(output)
                except StopIteration:
                    return 0  # indicate EOF

            # tell should be implemented for GCS
            def tell(self):
                return self.count

        return io.BufferedReader(IterStream(), buffer_size=io.DEFAULT_BUFFER_SIZE)
