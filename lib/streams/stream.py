from datetime import datetime
import time


class StreamCollection():

    _streams = []

    def list(self):
        return self._streams

    def add(self, stream):
        self._streams.append(stream)


class StreamBase():

    _name = None
    _content = None
    _gcs_url = None
    _extension = ""
    _mime_type = "application/octet-stream"

    def __init__(self, name, content):
        self._name = self.stream_name(name)
        self._content = content

    def as_file():
        """
            Transform stream in a IO object.
        """
        raise NotImplementedError

    def readline():
        """
            Yield each element of a stream, one by one. 
            (ex: line by line for file)
        """
        for line in self._content:
            yield line

    def stream_name(self, name):
        ts = time.time()
        ts_as_string = datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        return '{}_{}'.format(name, ts_as_string)

    def set_gcs_url(self, gcs_url):
        self._gcs_url = gcs_url

    def get_gcs_url(self):
        return self._gcs_url

    @property
    def name(self):
        return '{}{}'.format(self._name, self.extension())

    @property
    def content(self):
        return self._content

    @property
    def type(self):
        return self._mime_type

    def extension(self):
        return self._extension
