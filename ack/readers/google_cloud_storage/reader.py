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

import urllib

from google.cloud import storage
from ack.clients.google.client import GoogleClient
from ack.readers.object_storage.reader import ObjectStorageReader


class GoogleCloudStorageReader(ObjectStorageReader, GoogleClient):
    def __init__(self, bucket, prefix, format, dest_key_split=-1, **kwargs):
        super().__init__(bucket, prefix, format, dest_key_split, platform="GCS", **kwargs)

    def create_client(self, config):
        return storage.Client(credentials=self._get_credentials(), project=config.project_id)

    def create_bucket(self, client, bucket):
        return client.bucket(bucket)

    def list_objects(self, bucket, prefix):
        return bucket.list_blobs(prefix=prefix)

    @staticmethod
    def get_timestamp(_object):
        return _object.updated

    @staticmethod
    def get_key(_object):
        return urllib.parse.unquote(_object.path).split("o/", 1)[-1]

    @staticmethod
    def to_object(_object):
        return _object

    @staticmethod
    def download_object_to_file(_object, temp):
        _object.download_to_file(temp)
