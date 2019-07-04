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


GCS_MAX_TIMESTAMP_STATE_KEY = "gcs_max_timestamp"
GCS_MAX_FILES_STATE_KEY = "gcs_max_files"


@click.command(name="read_gcs")
@click.option("--gcs-bucket", required=True)
@click.option("--gcs-prefix", required=True, multiple=True)
@click.option("--gcs-format", required=True, type=click.Choice(['csv']))
@click.option("--gcs-key-filter")
@click.option("--gcs-csv-delimiter", default=",")
@processor()
def gcs(**kwargs):
    return GCSReader(**extract_args('gcs_', kwargs))


class GCSReader(Reader):

    def __init__(self, bucket, prefix, format, key_filter, **kwargs):
        self._client = storage.Client(project=config.PROJECT_ID)
        self._bucket = self._client.bucket(bucket)
        self._prefix = prefix
        self._key_filter = key_filter

        if format == 'csv':
            self._reader = self._make_csv_reader(**kwargs)

    def read(self):

        for prefix in self._prefix:

            blobs_sorted_by_time = sorted(self._bucket.list_blobs(prefix=prefix), key=lambda b: b.updated)

            for blob in blobs_sorted_by_time:

                logging.info("Found GCS file %s", blob.path)

                if self.has_already_processed_blob(blob):
                    logging.info("Skipping already processed file %s", blob.path)
                    continue

                def result_generator():
                    temp = tempfile.TemporaryFile()
                    blob.download_to_file(temp)

                    for record in self._reader(temp):
                        yield record

                    self.checkpoint_blob(blob)

                name = os.path.basename(blob.path)

                yield NormalizedJSONStream(name, result_generator())

    def has_already_processed_blob(self, blob):

        assert blob.updated is not None

        max_timestamp = self.state.get(GCS_MAX_TIMESTAMP_STATE_KEY)

        # We haven't seen any files before
        if not max_timestamp:
            return False

        # The most recent file is more recent than this one
        if max_timestamp > blob.updated:
            return True

        # The most recent file is less recent than this one
        if max_timestamp < blob.updated:
            return False

        # If the timestamp is the same, then check if we kept it
        if max_timestamp == blob.updated:
            max_files = self.state.get(GCS_MAX_FILES_STATE_KEY)
            return blob.path in max_files

    def checkpoint_blob(self, blob):

        assert blob.updated is not None

        max_timestamp = self.state.get(GCS_MAX_TIMESTAMP_STATE_KEY)

        assert blob.updated >= max_timestamp

        if not max_timestamp or max_timestamp < blob.updated:
            self.state.set(GCS_MAX_TIMESTAMP_STATE_KEY, blob.updated)
            self.state.set(GCS_MAX_FILES_STATE_KEY, [blob.path])
            return

        if max_timestamp == blob.updated:
            max_files = self.state.get(GCS_MAX_FILES_STATE_KEY)
            max_files.append(blob.updated)
            self.state.set(GCS_MAX_FILES_STATE_KEY, max_files)
            return

    @staticmethod
    def _make_csv_reader(csv_delimiter):

        def read_csv(fd):
            fd.seek(0)
            return csv.DictReader(fd, delimiter=str(csv_delimiter))

        return read_csv
