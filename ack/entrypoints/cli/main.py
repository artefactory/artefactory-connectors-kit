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

from ack.writers.writer import Writer
from ack.entrypoints.cli.writers import writers
from ack.readers.reader import Reader
from ack.entrypoints.cli.readers import readers
from ack.streams.json_stream import JSONStream
from ack.streams.normalized_json_stream import NormalizedJSONStream


@click.group(chain=True)
@click.option(
    "--normalize-keys",
    default=False,
    help="(Optional) If set to true, will normalize output keys, removing white spaces and special characters.",
    type=bool,
)
def cli(normalize_keys):
    pass


def build_commands(cli, available_commands):
    for cmd in available_commands:
        cli.add_command(cmd)


@cli.resultcallback()
def process_command_pipeline(provided_commands, normalize_keys):
    cmd_instances = [cmd() for cmd in provided_commands]
    provided_readers = list(filter(lambda o: isinstance(o, Reader), cmd_instances))
    provided_writers = list(filter(lambda o: isinstance(o, Writer), cmd_instances))

    _validate_provided_commands(provided_readers, provided_writers)

    reader = provided_readers[0]
    for stream in reader.read():
        for writer in provided_writers:
            if normalize_keys and issubclass(stream.__class__, JSONStream):
                writer.write(NormalizedJSONStream.create_from_stream(stream))
            else:
                writer.write(stream)


def _validate_provided_commands(provided_readers, provided_writers):
    if len(provided_readers) < 1:
        raise click.BadParameter("You must specify a reader")
    if len(provided_readers) > 1:
        raise click.BadParameter("You cannot specify multiple readers")
    if len(provided_writers) < 1:
        raise click.BadParameter("You must specify at least one writer")


if __name__ == "__main__":
    available_commands = readers + writers
    build_commands(cli, available_commands)
    cli()
