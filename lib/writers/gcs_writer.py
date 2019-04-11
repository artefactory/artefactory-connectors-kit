from config import logging

from google.cloud import storage

from lib.writers.writer import BaseWriter


class GCSWriter(BaseWriter):

    _client = storage.Client()

    def __init__(self, bucket="raw", folder=None):
        self._bucket = GCSBucket(self._client, bucket)
        self._folder = folder

    def write(self, stream):
        """
            Write file into GCS Bucket

            attr:
                filename (str): Filename to save in GCS
                content (File handler): File object to be duplicate in GCS
            return:
                gcs_path (str): Path to file {bucket}/{folder}/{file_name}
        """
        logging.info("Writing file on GCS")
        blob = self.create_file(stream.name)
        blob.upload_from_file(stream.as_file(), content_type=stream.type)

        gcs_url = self.gcs_path(stream.name)
        stream.set_gcs_url(gcs_url)
        logging.info("Uploading file at {}".format(gcs_url))
        return stream

    def create_file(self, name):
        filename = self.location(name)
        return self._bucket.get_file(filename)

    def gcs_path(self, name):
        file_path = self.location(name)
        return 'gs://{}'.format(self.format_path(self._bucket.name, file_path))

    def location(self, name):
        if self._folder is not None:
            return self.format_path(self._folder, name)
        return name

    def format_path(self, first, second):
        return '{}/{}'.format(first, second)


class GCSBucket():

    def __init__(self, gcs_client, name):
        self._client = gcs_client
        self._name = self.prefix_name(name)

    def get_file(self, file_name):
        return self.get_or_create().blob(file_name)

    def get_or_create(self):
        if self._name not in GCSBucket.list(self._client):
            logging.info("Creating bucket {}".format(self._name))
            self.create()
        logging.info("Getting bucket {}".format(self._name))
        return self.get()

    def get(self):
        return self._client.get_bucket(self._name)

    def create(self):
        bucket = self._client.bucket(bucket_name)
        bucket.location = "EU"
        bucket.create()

    def prefix_name(self, name):
        project_name = self._client.project
        return '{}-{}'.format(project_name, name)

    @property
    def name(self):
        return self._name

    @staticmethod
    def list(gcs_client):
        return [bucket.name for bucket in gcs_client.list_buckets()]
