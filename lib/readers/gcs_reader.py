import click

from google.cloud import storage
from lib.commands.command import processor
from lib.readers.objectstorage_reader import ObjectStorageReader
from lib.utils.args import extract_args
from lib.helpers.google_base import Google_Base_Class
import urllib


@click.command(name="read_gcs")
@click.option("--gcs-bucket", required=True)
@click.option("--gcs-prefix", required=True, multiple=True)
@click.option("--gcs-format", required=True, type=click.Choice(['csv', 'gz']))
@click.option("--gcs-dest-key-split", default=-1, type=int)
@click.option("--gcs-csv-delimiter", default=",")
@click.option("--gcs-csv-fieldnames", default=None)
@processor()
def gcs(**kwargs):
    return GCSReader(**extract_args('gcs_', kwargs))


class GCSReader(ObjectStorageReader, Google_Base_Class):

    def __init__(self, bucket, prefix, format, dest_key_split=-1, **kwargs):
        super().__init__(bucket, prefix, format, dest_key_split, platform="GCS",
                         **kwargs)

    def create_client(self, config):
        return storage.Client(credentials=self._get_credentials(),
                              project=config.project_id)

    def create_bucket(self, client, bucket):
        return client.bucket(bucket)

    def list_objects(self, bucket, prefix):
        return bucket.list_blobs(prefix=prefix)

    @staticmethod
    def get_timestamp(_object):
        return _object.updated

    @staticmethod
    def get_key(_object):
        return urllib.parse.unquote(_object.path).split('o/', 1)[-1]

    @staticmethod
    def to_object(_object):
        return _object

    @staticmethod
    def download_object_to_file(_object, temp):
        _object.download_to_file(temp)
