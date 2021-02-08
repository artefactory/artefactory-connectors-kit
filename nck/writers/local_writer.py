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
from nck.config import logger
import os

from nck.writers.writer import Writer
from nck.commands.command import processor


@click.command(name="write_local")
@click.option("--local-directory", "-d", required=True, help="Destination directory")
@click.option("--file-name", "-n", help="Destination file name")
@processor()
def local(**kwargs):
    return LocalWriter(**kwargs)


class LocalWriter(Writer):
    def __init__(self, local_directory, file_name):
        self._local_directory = local_directory
        self._file_name = file_name

    def write(self, stream):
        """
            Write file to disk at location given as parameter.
        """
        file_name = self._file_name or stream.name
        path = os.path.join(self._local_directory, file_name)

        logger.info(f"Writing stream {file_name} to {path}")
        file = stream.as_file()
        with open(path, "wb") as h:
            while True:
                buffer = file.read(1024)
                if len(buffer) > 0:
                    h.write(buffer)
                else:
                    break
