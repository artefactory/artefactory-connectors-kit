import config
import os
import tempfile
import logging

from lib.readers.reader import Reader
from lib.streams.normalized_json_stream import NormalizedJSONStream
import lib.utils.file_reader as file_reader


class ObjectStorageReader(Reader):

    def __init__(self, bucket, prefix, file_format, dest_key_split=-1, platform=None, **kwargs):
        self._client = self.create_client(config)
        self._bucket = self.create_bucket(self._client, bucket)
        self._prefix = prefix
        self._platform = platform

        self._format = file_format

        if self._format in file_reader.FileReader.__members__:
            for r in [file_reader.CSVReader, file_reader.GZIPReader]:
                if self._format == r.TAG.value:
                    self._reader = r(**kwargs).get_csv_reader()
                    break
        else:
            raise NotImplementedError(
                "The file format %s has not been implemented for reading yet." % str(self._format))

        self._dest_key_split = dest_key_split

        self.MAX_TIMESTAMP_STATE_KEY = "{}_max_timestamp".format(self._platform).lower()
        self.MAX_FILES_STATE_KEY = "{}_max_files".format(self._platform).lower()

    def read(self):

        for prefix in self._prefix:

            objects_sorted_by_time = sorted(self.list_objects(bucket=self._bucket, prefix=prefix),
                                            key=lambda o: self.get_timestamp(o))

            for o in objects_sorted_by_time:

                o = self.to_object(o)

                logging.info("Found %s file %s" % (self._platform, self.get_key(o)))

                if not self.compatible_object(o):
                    logging.info("Wrong extension: Skipping file %s", self.get_key(o))
                    continue

                if self.has_already_processed_object(o):
                    logging.info("Skipping already processed file %s", self.get_key(o))
                    continue

                def result_generator():
                    temp = tempfile.TemporaryFile()
                    self.download_object_to_file(o, temp)

                    for record in self._reader(temp):
                        yield record

                    self.checkpoint_object(o)

                name = self.get_key(o).split('/', self._dest_key_split)[-1]

                yield NormalizedJSONStream(name, result_generator())

    def compatible_object(self, o):
        return self.get_key(o).endswith('.' + self._format)

    def has_already_processed_object(self, o):

        assert self.get_timestamp(o) is not None

        max_timestamp = self.state.get(self.MAX_TIMESTAMP_STATE_KEY)

        # We haven't seen any files before
        if not max_timestamp:
            return False

        # The most recent file is more recent than this one
        if max_timestamp > self.get_timestamp(o):
            return True

        # The most recent file is less recent than this one
        if max_timestamp < self.get_timestamp(o):
            return False

        # If the timestamp is the same, then check if we kept it
        if max_timestamp == self.get_timestamp(o):
            max_files = self.state.get(self.MAX_FILES_STATE_KEY)
            return self.get_key(o) in max_files

    def checkpoint_object(self, o):

        assert self.get_timestamp(o) is not None

        max_timestamp = self.state.get(self.MAX_TIMESTAMP_STATE_KEY)

        if max_timestamp:
            assert self.get_timestamp(o) >= max_timestamp

        if not max_timestamp or max_timestamp < self.get_timestamp(o):
            self.state.set(self.MAX_TIMESTAMP_STATE_KEY, self.get_timestamp(o))
            self.state.set(self.MAX_FILES_STATE_KEY, [self.get_key(o)])
            return

        if max_timestamp == self.get_timestamp(o):
            max_files = self.state.get(self.MAX_FILES_STATE_KEY)
            max_files.append(self.get_timestamp(o))
            self.state.set(self.MAX_FILES_STATE_KEY, max_files)
            return

    def create_client(self, config):
        raise NotImplementedError

    def create_bucket(self, client, bucket):
        raise NotImplementedError

    def list_objects(self, bucket, prefix):
        raise NotImplementedError

    @staticmethod
    def get_timestamp(o):
        raise NotImplementedError

    @staticmethod
    def get_key(o):
        raise NotImplementedError

    @staticmethod
    def to_object(o):
        raise NotImplementedError

    @staticmethod
    def download_object_to_file(o, temp):
        raise NotImplementedError
