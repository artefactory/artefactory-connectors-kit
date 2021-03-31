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

from ack.config import logger
from ack.writers import Writer

# from ack.utils.retry import retry


class ObjectStorageWriter(Writer):
    def __init__(self, bucket_name, prefix=None, file_name=None, platform=None, **kwargs):
        self._bucket_name = bucket_name
        self._prefix = prefix if prefix else ""
        self._file_name = file_name
        self._platform = platform
        self._bucket = self._get_bucket_if_exist()

    def write(self, stream):
        logger.info(f"Start writing file to {self._platform} ...")
        self._set_valid_file_name(stream.name)
        final_name = os.path.join(self._prefix, self._file_name)
        self._write_aux(stream, final_name)

    def _write_aux(self, stream, final_name):
        self._create_blob(final_name, stream)
        logger.info(f"Wrote {final_name} file to {self._bucket_name} on  {self._platform} ...")
        uri = self._get_uri(final_name)
        logger.info(f"file can be found at {uri}")

    def _get_bucket_if_exist(self):
        client = self._create_client()
        bucket = self._create_bucket(client)
        list_buckets_names = [bucket.name for bucket in self._list_buckets(client)]
        try:
            assert self._bucket_name in list_buckets_names
        except AssertionError as err:
            raise Exception(
                f"{self._bucket_name} bucket does not exist. available buckets are {list_buckets_names}"
            ).with_traceback(err.__traceback__)
        return bucket

    def _get_file_path(self, file_name):
        return f"://{self._bucket_name}/{file_name}"

    def _set_valid_file_name(self, stream_name):
        file_format = os.path.splitext(stream_name)[-1]
        self._file_name = f"{self._file_name}{file_format}" if self._file_name is not None else stream_name

    def _create_client(self):
        return NotImplementedError

    def _create_bucket(self, client):
        return NotImplementedError

    def _list_buckets(self, client):
        return NotImplementedError

    def _create_blob(self, file_name, stream):
        return NotImplementedError

    def _get_uri(self, file_name):
        return NotImplementedError
