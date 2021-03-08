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

import click
from google.cloud import storage
from nck import config
from nck.commands.command import processor
from nck.helpers.google_base import GoogleBaseClass
from nck.utils.args import extract_args
from nck.writers.objectstorage_writer import ObjectStorageWriter


@click.command(name="write_gcs")
@click.option("--gcs-bucket", help="GCS Bucket", required=True)
@click.option("--gcs-prefix", help="GCS path to write the file.")
@click.option("--gcs-project-id", help="GCS Project Id")
@click.option(
    "--gcs-filename",
    help="Override the default name of the file (don't add the extension)",
)
@processor()
def gcs(**kwargs):
    return GCSWriter(**extract_args("gcs_", kwargs))


class GCSWriter(ObjectStorageWriter, GoogleBaseClass):
    def __init__(self, bucket, project_id, prefix=None, filename=None, **kwargs):
        self._project_id = self.get_project_id(project_id)
        super().__init__(bucket, prefix, filename, platform="GCS", **kwargs)

    def _create_client(self):
        return storage.Client(credentials=self._get_credentials(), project=self._project_id)

    def _create_bucket(self, client):
        return client.bucket(self._bucket_name)

    def _list_buckets(self, client):
        return client.list_buckets()

    def _create_blob(self, file_name, stream):
        blob = self._bucket.blob(file_name)
        blob.upload_from_file(stream.as_file(), content_type=stream.mime_type)

    def _get_uri(self, file_name):
        return f"gs{self._get_file_path(file_name)}"

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
