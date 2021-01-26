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

from nck.readers import Reader, readers
from nck.streams.json_stream import JSONStream
from nck.streams.normalized_json_stream import NormalizedJSONStream
from nck.writers import Writer, writers


@click.group(chain=True)
@click.option(
    "--normalize-keys",
    default=False,
    help="(Optional) If set to true, will normalize output keys, removing white spaces and special characters.",
    type=bool,
)
def app(normalize_keys):
    pass


@app.resultcallback()
def run(processors, normalize_keys):
    processor_instances = [p() for p in processors]

    _readers = list(filter(lambda o: isinstance(o, Reader), processor_instances))
    _writers = list(filter(lambda o: isinstance(o, Writer), processor_instances))

    if len(_readers) < 1:
        raise click.BadParameter("You must specify a reader")

    if len(_readers) > 1:
        raise click.BadParameter("You cannot specify multiple readers")

    if len(_writers) < 1:
        raise click.BadParameter("You must specify at least one writer")

    reader = _readers[0]
    # A stream should represent a full file!
    for stream in reader.read():
        for writer in _writers:
            if normalize_keys and issubclass(stream.__class__, JSONStream):
                writer.write(NormalizedJSONStream.create_from_stream(stream))
            else:
                writer.write(stream)


def cli_entrypoint():
    build_commands()
    app()


def build_commands():
    for writer in writers:
        app.add_command(writer)

    for reader in readers:
        app.add_command(reader)


if __name__ == "__main__":
    build_commands()
    app()
