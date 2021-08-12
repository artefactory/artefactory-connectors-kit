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
from ack.writers.file_writer.writer import FileWriter


class LocalWriter(FileWriter):
    def __init__(self, directory, file_name, file_format):
        self._directory = directory
        self._file_name = file_name
        super().__init__(file_format)

    def write(self, stream):
        """
        Write file to disk at location given as parameter.
        """
        file_name = self._file_name or stream.name
        path = os.path.join(self._directory, file_name)

        logger.info(f"Writing stream {file_name} to {path}")
        logger.info(f"file format: {self._file_format}")
        file = stream.as_file()
        with open(path, "wb") as h:
            while True:
                buffer = file.read(1024)
                if len(buffer) > 0:
                    h.write(buffer)
                else:
                    break
