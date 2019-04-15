from config import logging

from lib.writers.bigquery_writer import BigQueryWriter
from lib.writers.gcs_writer import GCSWriter


class Builder():

    _reader = None
    _saver = None

    def __init__(self, reader, gcs_writer_args, bq_writer_args):
        self._reader = reader
        self._gcs_writer = GCSWriter(**gcs_writer_args)
        self._bq_writer = BigQueryWriter(**bq_writer_args)

    def execute(self):
        logging.info("Execution is loading")
        for stream in self._reader.collection():
            updated_stream = self._gcs_writer.write(stream)
            self._bq_writer.write(updated_stream)
            self.save(updated_stream.name)

    def save(self, content):
        if self._saver is not None:
            return self._saver.add_checkpoint(content)
        return None
