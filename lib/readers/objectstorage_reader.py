import config
import tempfile
import logging


from lib.readers.reader import Reader
from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.utils.file_reader import FileEnum


def find_reader(_format, kwargs):
    _format = _format.upper()
    if _format in FileEnum.__members__:
        r = getattr(FileEnum, _format).value
        _reader = r(**kwargs).get_csv_reader()
    else:
        raise NotImplementedError(
            f'The file format {str(_format)} has not been implemented for reading yet.')
    return _reader

def no_files_seen_before(max_timestamp):
    return not max_timestamp


def _object_older_than_most_recently_ingested_file(max_timestamp, _object_timestamp):
    return max_timestamp > _object_timestamp


def _object_newer_than_most_recently_ingested_file(max_timestamp, _object_timestamp):
    return max_timestamp < _object_timestamp


def _object_as_old_as_most_recently_ingested_file(max_timestamp, _object_timestamp):
    return max_timestamp == _object_timestamp


class ObjectStorageReader(Reader):

    def __init__(self, bucket, prefix, file_format, dest_key_split, platform=None, **kwargs):
        self._client = self.create_client(config)
        self._bucket = self.create_bucket(self._client, bucket)
        self._prefix_list = prefix
        self._platform = platform

        self._format = file_format
        self._reader = find_reader(self._format, kwargs)
        self._dest_key_split = dest_key_split

        self.MAX_TIMESTAMP_STATE_KEY = f'{self._platform}_max_timestamp'.lower()
        self.MAX_FILES_STATE_KEY = f'{self._platform}_max_files'.lower()

    def read(self):

        for prefix in self._prefix_list:

            objects_sorted_by_time = sorted(self.list_objects(bucket=self._bucket, prefix=prefix),
                                            key=lambda o: self.get_timestamp(o))

            for _object in objects_sorted_by_time:

                _object = self.to_object(_object)

                logging.info(f'Found {self._platform} file {self.get_key(_object)}')

                if not self.is_compatible_object(_object):
                    logging.info(f'Wrong extension: Skipping file {self.get_key(_object)}')
                    continue

                if self.has_already_processed_object(_object):
                    logging.info(f'Skipping already processed file {self.get_key(_object)}')
                    continue

                def result_generator():
                    temp = tempfile.TemporaryFile()
                    self.download_object_to_file(_object, temp)

                    for record in self._reader(temp):
                        yield record

                    self.checkpoint_object(_object)

                name = self.get_key(_object).split('/', self._dest_key_split)[-1]

                yield NormalizedJSONStream(name, result_generator())

    def is_compatible_object(self, _object):
        return self.get_key(_object).endswith('.' + self._format)

    def has_already_processed_object(self, _object):

        assert self.get_timestamp(_object) is not None, 'Object has no timestamp!'

        max_timestamp = self.state.get(self.MAX_TIMESTAMP_STATE_KEY)

        if no_files_seen_before(max_timestamp):
            return False

        _object_timestamp = self.get_timestamp(_object)

        if _object_older_than_most_recently_ingested_file(max_timestamp, _object_timestamp):
            return True

        if _object_newer_than_most_recently_ingested_file(max_timestamp, _object_timestamp):
            return False

        if _object_as_old_as_most_recently_ingested_file(max_timestamp, _object_timestamp):
            max_files = self.state.get(self.MAX_FILES_STATE_KEY)
            return self.get_key(_object) in max_files

    def checkpoint_object(self, _object):

        assert self.get_timestamp(_object) is not None, 'Object has no timestamp!'

        max_timestamp = self.state.get(self.MAX_TIMESTAMP_STATE_KEY)
        _object_timestamp = self.get_timestamp(_object)

        if max_timestamp and _object_older_than_most_recently_ingested_file(max_timestamp, _object_timestamp):
            raise RuntimeError('Object is older than max timestamp at checkpoint time')

        elif not max_timestamp or _object_newer_than_most_recently_ingested_file(max_timestamp, _object_timestamp):
            self.update_max_timestamp(_object_timestamp, _object)

        else:
            assert _object_as_old_as_most_recently_ingested_file(max_timestamp, _object_timestamp)
            self.update_max_files(_object)

    def update_max_timestamp(self, _object_timestamp, _object):
        self.state.set(self.MAX_TIMESTAMP_STATE_KEY, _object_timestamp)
        self.state.set(self.MAX_FILES_STATE_KEY, [self.get_key(_object)])

    def update_max_files(self, _object):
        max_files = self.state.get(self.MAX_FILES_STATE_KEY)
        max_files.append(self.get_key(_object))
        self.state.set(self.MAX_FILES_STATE_KEY, max_files)

    def create_client(self, config):
        raise NotImplementedError

    def create_bucket(self, client, bucket):
        raise NotImplementedError

    def list_objects(self, bucket, prefix):
        raise NotImplementedError

    @staticmethod
    def get_timestamp(_object):
        raise NotImplementedError

    @staticmethod
    def get_key(_object):
        raise NotImplementedError

    @staticmethod
    def to_object(_object):
        raise NotImplementedError

    @staticmethod
    def download_object_to_file(_object, temp):
        raise NotImplementedError
