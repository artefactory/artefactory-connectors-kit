import click
import config
import os
import tempfile
import csv
import logging

from google.cloud import storage
from lib.commands.command import processor
from lib.readers.reader import Reader
from lib.utils.args import extract_args
from lib.streams.normalized_json_stream import NormalizedJSONStream


@click.command(name="read_gcs")
@click.option("--gcs-bucket", required=True)
@click.option("--gcs-prefix", required=True, multiple=True)
@click.option("--gcs-format", required=True, type=click.Choice(['csv']))
@click.option("--gcs-csv-delimiter", default=",")
@processor
def gcs(**kwargs):
    return GCSReader(**extract_args('gcs_', kwargs))


class GCSReader(Reader):

    def __init__(self, bucket, prefix, format, **kwargs):
        self._client = storage.Client(project=config.PROJECT_ID)
        self._bucket = self._client.bucket(bucket)
        self._prefix = prefix

        if format == 'csv':
            self._reader = self._make_csv_reader(**kwargs)

    def read(self):

        for prefix in self._prefix:
            for blob in self._bucket.list_blobs(prefix=prefix):

                logging.info("Found GCS File %s", blob.path)

                def result_generator():
                    temp = tempfile.TemporaryFile()
                    blob.download_to_file(temp)

                    for record in self._reader(temp):
                        yield record

                name = os.path.basename(blob.path)

                yield NormalizedJSONStream(name, result_generator())

    @staticmethod
    def _make_csv_reader(csv_delimiter):

        def read_csv(fd):
            fd.seek(0)
            return csv.DictReader(fd, delimiter=str(csv_delimiter))

        return read_csv
