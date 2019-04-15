from lib.streams.stream import StreamBase


class FileStream(StreamBase):

    def as_file(self):
        return self._content()

    def readline(self):
        file = open(self.as_file())
        for line in f:
            yield line
        file.close()
