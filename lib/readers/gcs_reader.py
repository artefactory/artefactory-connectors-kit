import click
import logging

from google.cloud import storage
from lib.commands.command import processor
from lib.readers.objectstorage_reader import ObjectStorageReader
from lib.utils.args import extract_args

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


class GCSReader(ObjectStorageReader):

    def __init__(self, bucket, prefix, format, dest_key_split, **kwargs):
        super(GCSReader, self).__init__(bucket, prefix, format, dest_key_split, platform="GCS", **kwargs)

    def create_client(self, config):
        return storage.Client(project=config.PROJECT_ID)

    def create_bucket(self, client, bucket):
        return client.bucket(bucket)

    def list_objects(self, bucket, prefix):
        return bucket.list_blobs(prefix=prefix)

    @staticmethod
    def get_timestamp(o):
        return o.updated

    @staticmethod
    def get_key(o):
        return urllib.parse.unquote(o.path).split('o/', 1)[-1]

    @staticmethod
    def to_object(o):
        return o

    @staticmethod
    def download_object_to_file(o, temp):
        o.download_to_file(temp)
