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

from ack.streams.json_stream import JSONStream
from ack.streams.normalized_json_stream import NormalizedJSONStream
from ack.utils.file_reader import read_json
from ack.utils.formatter import format_reader, format_writers


@click.command()
@click.option(
    "--config-file", help="Path of the json file used to build the command.", required=True, type=click.Path(exists=True),
)
def read_and_write_from_json(config_file):
    data = read_json(config_file)
    read_and_write(data)


def read_and_write(data):
    if "normalize_keys" not in data.keys():
        data["normalize_keys"] = False

    reader = format_reader(data["reader"])
    writers = format_writers(data["writers"])

    for stream in reader.read():
        for writer in writers:
            if data["normalize_keys"] and issubclass(stream.__class__, JSONStream):
                writer.write(NormalizedJSONStream.create_from_stream(stream))
            else:
                writer.write(stream)


if __name__ == "__main__":
    read_and_write()
