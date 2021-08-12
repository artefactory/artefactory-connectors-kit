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
from ack import config
from ack.clients.google.client import GoogleClient
from ack.writers.object_storage.writer import ObjectStorageWriter


class GoogleCloudStorageWriter(ObjectStorageWriter, GoogleClient):
    def __init__(self, bucket, project_id, prefix=None, file_name=None, **kwargs):
        self._project_id = self.get_project_id(project_id)
        super().__init__(bucket, prefix, file_name, platform="GCS", **kwargs)

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
                    "Please provide a project id in ENV var or params.", param_type="--gcs-project-id",
                )
        return project_id
