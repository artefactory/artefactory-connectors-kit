import logging


class Runner(object):

    _reader = None

    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer

    def run(self):
        logging.info("Runner started")

        for stream in self._reader.read():
            self._writer.write(stream)
