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

from io import BytesIO

from nck import config
from nck.config import logger
from nck.readers.reader import Reader
from nck.streams.new_stream import NewStream


class ObjectStorageReader(Reader):
    def __init__(self, bucket, prefix, file_format, dest_key_split, platform=None, **kwargs):
        self._client = self.create_client(config)
        self._bucket = self.create_bucket(self._client, bucket)
        self._prefix_list = prefix
        self._platform = platform

        self._format = file_format
        self._dest_key_split = dest_key_split

    def read(self):

        for prefix in self._prefix_list:

            objects_sorted_by_time = sorted(
                self.list_objects(bucket=self._bucket, prefix=prefix), key=lambda o: self.get_timestamp(o),
            )

            for _object in objects_sorted_by_time:

                _object = self.to_object(_object)

                logger.info(f"Found {self._platform} file {self.get_key(_object)}")

                if not self.is_compatible_object(_object):
                    logger.info(f"Wrong extension: Skipping file {self.get_key(_object)}")
                    continue

                name = self.get_key(_object).split("/", self._dest_key_split)[-1]

                yield NewStream(name, self._dowload_to_stream(_object))

    def _dowload_to_stream(self, _object):
        f = BytesIO()
        self.download_object_to_file(_object, f)
        return f

    def is_compatible_object(self, _object):
        return self.get_key(_object).endswith("." + self._format)

    def create_client(self, config):
        raise NotImplementedError

    def create_bucket(self, client, bucket):
        raise NotImplementedError

    def list_objects(self, bucket, prefix):
        raise NotImplementedError

    @staticmethod
    def get_timestamp(_object):
        raise NotImplementedError

    @staticmethod
    def get_key(_object):
        raise NotImplementedError

    @staticmethod
    def to_object(_object):
        raise NotImplementedError

    @staticmethod
    def download_object_to_file(_object, temp):
        raise NotImplementedError
