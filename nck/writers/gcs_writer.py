import config
import logging
import os
from nck.helpers.google_base import GoogleBaseClass
import click

from nck.writers.writer import Writer
from nck.commands.command import processor
from nck.utils.args import extract_args
from google.cloud import storage


@click.command(name="write_gcs")
@click.option("--gcs-bucket", help="GCS Bucket", required=True)
@click.option("--gcs-prefix", help="GCS path to write the file.")
@click.option("--gcs-project-id", help="GCS Project Id")
@click.option(
    "--gcs-file-name",
    help="Override the default name of the file (don't add the extension)",
)
@processor()
def gcs(**kwargs):
    return GCSWriter(**extract_args("gcs_", kwargs))


class GCSWriter(Writer, GoogleBaseClass):
    _client = None

    def __init__(self, bucket, project_id, prefix=None, file_name=None):
        project_id = self.get_project_id(project_id)
        self._client = storage.Client(
            credentials=self._get_credentials(), project=project_id
        )
        self._bucket = self._client.bucket(bucket)
        self._prefix = prefix
        self._file_name = file_name

    def write(self, stream):
        """
            Write file into GCS Bucket

            attr:
                stream: Stream with the file content.
            return:
                gcs_path (str): Path to file {bucket}/{prefix}{file_name}
        """
        logging.info("Writing file to GCS")
        _, extension = self._extract_extension(stream.name)
        file_name = (
            self._extract_extension(self._file_name)[0] + extension
            if self._file_name is not None
            else stream.name
        )
        blob = self.create_blob(file_name)
        blob.upload_from_file(stream.as_file(), content_type=stream.mime_type)
        uri = self.uri_for_name(file_name)

        logging.info("Uploaded file to {}".format(uri))

        return uri, blob

    def create_blob(self, name):
        filename = self.path_for_name(name)
        return self._bucket.blob(filename)

    def uri_for_name(self, name):
        path = self.path_for_name(name)
        return "gs://{bucket}/{path}".format(bucket=self._bucket.name, path=path)

    def path_for_name(self, name):
        if self._prefix:
            return os.path.join(self._prefix, name)
        return name

    @staticmethod
    def _extract_extension(full_file_name: str):
        """Returns a tuple: file_name, extension"""
        return os.path.splitext(full_file_name)

    @staticmethod
    def get_project_id(project_id):
        if project_id is None:
            try:
                return config.PROJECT_ID
            except Exception:
                raise click.exceptions.MissingParameter(
                    "Please provide a project id in ENV var or params.",
                    param_type="--gcs-project-id",
                )
        return project_id
