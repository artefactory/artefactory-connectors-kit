import click
import config
import os
import tempfile
import csv
import codecs
import logging

from google.cloud import storage
from lib.commands.command import processor
from lib.readers.objectstorage_reader import ObjectStorageReader
from lib.utils.args import extract_args


@click.command(name="read_gcs")
@click.option("--gcs-bucket", required=True)
@click.option("--gcs-prefix", required=True, multiple=True)
@click.option("--gcs-format", required=True, type=click.Choice(['csv']))
@click.option("--gcs-key-filter")
@click.option("--gcs-csv-delimiter", default=",")
@processor()
def gcs(**kwargs):
    return GCSReader(**extract_args('gcs_', kwargs))


class GCSReader(ObjectStorageReader):

    def __init__(self, bucket, prefix, format, **kwargs):
        super(GCSReader, self).__init__(bucket, prefix, format, platform="GCS", **kwargs)

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
        return o.path

    @staticmethod
    def to_object(o):
        return o

    @staticmethod
    def download_object_to_file(o, temp):
        o.download_to_file(temp)