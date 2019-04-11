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
        for element in self._reader.collection():
            updated_element = self._gcs_writer.write(element)
            self._bq_writer.write(updated_element)
            self.save(updated_element.name)

    def save(self, content):
        if self._saver is not None:
            return self._saver.add_checkpoint(content)
        return None
