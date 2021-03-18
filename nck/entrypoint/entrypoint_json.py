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

from nck.streams.json_stream import JSONStream
from nck.streams.normalized_json_stream import NormalizedJSONStream
from nck.utils.file_reader import read_json
from nck.utils.formatter import format_reader, format_writers


@click.command()
@click.option(
    "--config-file", help="Path of the json file used to build the command.", required=True, type=click.Path(exists=True),
)
def read_and_write(config_file):
    # args = parse_json_config_file_to_text(config_file)
    data = read_json(config_file)
    if "normalize_keys" not in data.keys():
        data["normalize_keys"] = False

    # get the instances for each reader/writer
    reader = format_reader(data["reader"])
    writers = format_writers(data["writers"])
    # read and then write
    for stream in reader.read():
        for writer in writers:
            if data["normalize_keys"] and issubclass(stream.__class__, JSONStream):
                writer.write(NormalizedJSONStream.create_from_stream(stream))
            else:
                writer.write(stream)


if __name__ == "__main__":
    # we need to catch SystemExit as every Click command ends with this Exception
    read_and_write()
