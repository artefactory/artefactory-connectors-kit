from datetime import datetime
import time
import io


class Stream(object):
    _name = None
    _source_generator = None
    _local_cache = None

    extension = None
    mime_type = "application/octet-stream"

    def __init__(self, name, source_generator):
        """
            _source_generator is a generator yielding dicts
        """
        self._name = self.create_stream_name(name)
        self._source_generator = source_generator
        self._iterator = iter(source_generator)
        self.leftover = ''

    def __len__(self):
        return self._source_generator.__len__()

    def __iter__(self):
        return self._iterator

    def as_file(self) -> io.BufferedReader:
        return self._iterable_to_stream(self._iterator, self.encode_record)

    def readlines(self):
        """
            Yield each element of a the generator, one by one.
            (ex: line by line for file)
        """
        for record in self._iterator:
            yield record

    @classmethod
    def create_from_stream(cls, source_stream):
        if isinstance(source_stream, cls):
            return source_stream

        return cls(source_stream.name, source_stream.readlines())

    @classmethod
    def encode_record(cls, record) -> bytes:
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

    @staticmethod
    def _iterable_to_stream(iterable, encode, buffer_size=io.DEFAULT_BUFFER_SIZE):
        """
        Lets you use an iterable (e.g. a generator) that yields bytestrings as a
        read-only
        input stream.

        The stream implements Python 3's newer I/O API (available in Python 2's io
        module).
        For efficiency, the stream is buffered.
        """

        class IterStream(io.RawIOBase):
            def __init__(self):
                self.leftover = None
                self.count = 0

            def readable(self):
                return True

            def readinto(self, b):
                try:
                    l = len(b)  # We're supposed to return at most this much
                    chunk = self.leftover or encode(next(iterable))
                    output, self.leftover = chunk[:l], chunk[l:]
                    b[:len(output)] = output
                    self.count += len(output)
                    return len(output)
                except StopIteration:
                    return 0  # indicate EOF

            # tell should be implemented for GCS
            def tell(self):
                return self.count

        return io.BufferedReader(IterStream(), buffer_size=buffer_size)
