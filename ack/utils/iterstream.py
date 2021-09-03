import io


class IterStream(io.RawIOBase):
    """
        Credit goes to 'Mechanical snail'
            at https://stackoverflow.com/questions/6657820/python-convert-an-iterable-to-a-stream

        Lets you use an iterable (e.g. a generator) that yields bytestrings as a
        read-only
        input stream.

        The stream implements Python 3's newer I/O API (available in Python 2's io
        module).
        For efficiency, the stream is buffered.
    """
    def __init__(self, encode, iterable):
        self.leftover = None
        self.count = 0
        self.encode = encode
        self.iterable = iterable

    def readable(self):
        return True

    def readinto(self, b):
        try:
            chunk_length = len(b)  # We're supposed to return at most this much
            chunk = self.leftover or self.encode(next(self.iterable))
            output, self.leftover = chunk[:chunk_length], chunk[chunk_length:]
            b[: len(output)] = output
            self.count += len(output)
            return len(output)
        except StopIteration:
            return 0  # indicate EOF

    # tell should be implemented for GCS
    def tell(self):
        return self.count
