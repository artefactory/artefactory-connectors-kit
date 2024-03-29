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
from typing import Dict, List

from ack.readers.reader import Reader
from ack.entrypoints.json.readers import readers_classes
from ack.writers.writer import Writer
from ack.entrypoints.json.writers import writers_classes


def format_reader(reader: Dict) -> Reader:
    reader_name = reader.pop("name")
    config = readers_classes[reader_name][1](**reader)
    return readers_classes[reader_name][0](**config.dict())


def format_writers(writers: List[Dict]) -> [Writer]:
    writers_list = []
    for writer in writers:
        writer_name = writer.pop("name")
        # if there is a config class/file => there is arguments
        if len(writers_classes[writer_name]) > 1:
            config = writers_classes[writer_name][1](**writer)
            writers_list.append(writers_classes[writer_name][0](**config.dict()))
        else:
            writers_list.append(writers_classes[writer_name][0]())

    return writers_list
