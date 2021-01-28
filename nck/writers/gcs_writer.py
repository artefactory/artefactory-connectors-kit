# GNU Lesser General Public License v3.0 only
# Copyright (C) 2020 Artefact
# licence-information@artefact.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import os

import click
from google.cloud import storage
from nck import config
from nck.commands.command import processor
from nck.config import logger
from nck.helpers.google_base import GoogleBaseClass
from nck.utils.args import extract_args
from nck.writers.writer import Writer


@click.command(name="write_gcs")
@click.option("--gcs-bucket", help="GCS Bucket", required=True)
@click.option("--gcs-prefix", help="GCS path to write the file.")
@click.option("--gcs-project-id", help="GCS Project Id")
@click.option(
    "--gcs-file-name", help="Override the default name of the file (don't add the extension)",
)
@processor()
def gcs(**kwargs):
    return GCSWriter(**extract_args("gcs_", kwargs))


class GCSWriter(Writer, GoogleBaseClass):
    _client = None

    def __init__(self, bucket, project_id, prefix=None, file_name=None):
        project_id = self.get_project_id(project_id)
        self._client = storage.Client(credentials=self._get_credentials(), project=project_id)
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
        logger.info("Writing file to GCS")
        _, extension = self._extract_extension(stream.name)
        file_name = self._extract_extension(self._file_name)[0] + extension if self._file_name is not None else stream.name
        blob = self.create_blob(file_name)
        blob.upload_from_file(stream.as_file(), content_type=stream.mime_type)
        uri = self.uri_for_name(file_name)

        logger.info("Uploaded file to {}".format(uri))

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
                    "Please provide a project id in ENV var or params.", param_type="--gcs-project-id",
                )
        return project_id
