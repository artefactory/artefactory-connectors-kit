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
from ack.writers.object_storage.writer import ObjectStorageWriter
from azure.storage.blob import BlobServiceClient


class AzureBlobStorageWriter(ObjectStorageWriter):
    def __init__(self, container, connection_string, file_format, prefix=None, filename=None, **kwargs):
        self.connection_string = connection_string
        super().__init__(container, file_format, prefix, filename, platform="Azure Blob Storage", **kwargs)

    def _create_client(self):
        return BlobServiceClient.from_connection_string(self.connection_string)

    def _create_bucket(self, client):
        return client.get_container_client(self._bucket_name)

    def _list_buckets(self, client):
        return client.list_containers()

    def _create_blob(self, file_name, stream):
        blob = self._bucket.get_blob_client(file_name)
        blob.upload_blob(self.formatter.format_stream_for_upload(stream))

    def _get_uri(self, file_name):
        return f"azure{self._get_file_path(file_name)}"
