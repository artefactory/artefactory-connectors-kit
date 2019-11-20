import config
import logging
import os
from lib.helpers.google_base import GoogleBaseClass
import click

from lib.writers.writer import Writer
from lib.commands.command import processor
from lib.utils.args import extract_args
from lib.utils.retry import retry
from google.cloud import storage


@click.command(name="write_gcs")
@click.option('--gcs-bucket', help="GCS Bucket", required=True)
@click.option('--gcs-prefix', help="GCS Prefix")
@click.option('--gcs-project-id', help="GCS Prefix")
@processor()
def gcs(**kwargs):
    return GCSWriter(**extract_args('gcs_', kwargs))


class GCSWriter(Writer, GoogleBaseClass):
    _client = None

    def __init__(self, bucket, project_id, prefix=None):
        project_id = self.get_project_id(project_id)
        self._client = storage.Client(credentials=self._get_credentials(),
                                      project=project_id)
        self._bucket = self._client.bucket(bucket)
        self._prefix = prefix

    @retry
    def write(self, stream):
        """
            Write file into GCS Bucket

            attr:
                filename (str): Filename to save in GCS
                content (File handle): File object to be copied to GCS
            return:
                gcs_path (str): Path to file {bucket}/{prefix}{file_name}
        """
        logging.info("Writing file to GCS")
        blob = self.create_blob(stream.name)
        blob.upload_from_file(stream.as_file(), content_type=stream.mime_type)

        uri = self.uri_for_name(stream.name)

        logging.info("Uploaded file to {}".format(uri))

        return uri, blob

    def create_blob(self, name):
        filename = self.path_for_name(name)
        return self._bucket.blob(filename)

    def uri_for_name(self, name):
        path = self.path_for_name(name)
        return 'gs://{bucket}/{path}'.format(bucket=self._bucket.name, path=path)

    def path_for_name(self, name):
        if self._prefix:
            return os.path.join(self._prefix, name)
        return name

    @staticmethod
    def get_project_id(project_id):
        if project_id is None:
            try:
                return config.PROJECT_ID
            except Exception:
                raise click.exceptions.MissingParameter(
                    'Please provide a project id in ENV var or params.',
                    param_type='--gcs-project-id')
        return project_id
