from datetime import datetime
import time
import tempfile
import logging


class Stream(object):

    _name = None
    _source_stream = None
    _local_cache = None

    extension = None
    mime_type = "application/octet-stream"

    def __init__(self, name, source_stream):
        """
            source_stream is a generator yielding dicts
        """
        self._name = self.create_stream_name(name)
        self._source_stream = source_stream

    def data(self):
        if not self._local_cache:
            self._local_cache = self._build_local_cache(self._source_stream)

        self._local_cache.seek(0)

        return self._local_cache

    def as_file(self):
        return self.data()

    def readlines(self):
        """
            Yield each element of a stream, one by one.
            (ex: line by line for file)
        """
        for record in self.data():
            yield self.decode_record(record)

    @classmethod
    def create_from_stream(cls, source_stream):
        if isinstance(source_stream, cls):
            return source_stream

        return cls(source_stream.name, source_stream.readlines())

    @classmethod
    def _build_local_cache(cls, source_stream):
        temp = tempfile.TemporaryFile()

        logging.debug("Spooling data to %s", temp)

        for record in source_stream:
            temp.write("{}\n".format(cls.encode_record(record)))

        temp.seek(0)
        return temp

    @classmethod
    def encode_record(cls, record):
        raise NotImplementedError

    @classmethod
    def decode_record(cls, record):
        raise NotImplementedError

    @staticmethod
    def create_stream_name(name):
        ts = time.time()
        ts_as_string = datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        return '{}_{}'.format(name, ts_as_string)

    @property
    def name(self):
        return '.'.join(filter(None, [self._name, self.extension]))
