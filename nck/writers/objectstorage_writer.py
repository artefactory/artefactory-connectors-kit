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

from nck.config import logger
from nck.writers import Writer
from nck.utils.retry import retry


class ObjectStorageWriter(Writer):
    def __init__(self, bucket, prefix=None, file_name=None, platform=None, **kwargs):
        self._bucket_name = bucket
        self._prefix = prefix if prefix else ""
        self._file_name = file_name
        self._platform = platform
        self.bucket = self._create_bucket()

    @retry
    def write(self, stream):
        logger.info(f"Start writing file to {self._platform} ...")
        file_name = self._file_name if self._file_name else stream.name
        final_name = os.path.join(self._prefix, file_name)
        self._create_blob(final_name)
        return self._get_uri(final_name)

    def _get_bucket_if_exist(self):
        client = self._create_client().Bucket(self._bucket_name)
        bucket = self._create_bucket(client)
        try:
            assert bucket in self._list_buckets(client)
        except AssertionError as err:
            logger.exception(f"{self._bucket_name} bucket does not exist.")
            raise err

        return bucket

    def _get_file_path(self, file_name):
        return f"://{self._bucket_name}/{file_name}"

    def _create_client(self):
        return NotImplementedError

    def _create_bucket(self, client):
        return NotImplementedError

    def _list_buckets(self, client):
        return NotImplementedError

    def _create_blob(self, file_name):
        return NotImplementedError

    def _get_uri(self, file_name):
        return NotImplementedError
