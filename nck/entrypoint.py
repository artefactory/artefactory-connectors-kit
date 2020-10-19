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

from nck.writers import writers, Writer
from nck.readers import readers, Reader
import nck.state_service as state
from nck.streams.normalized_json_stream import NormalizedJSONStream
from nck.streams.json_stream import JSONStream


@click.group(chain=True)
@click.option("--state-service-name")
@click.option("--state-service-host", help="Redis server IP address")
@click.option("--state-service-port", help="Redis server port", default=6379)
@click.option("--normalize-keys", default=False,
              help="(Optional) If set to true, will normalize the output files keys, removing "
                   "white spaces and special characters.", type=bool)
def app(state_service_name, state_service_host, state_service_port, normalize_keys):
    if (state_service_name or state_service_host) and not (
            state_service_name and state_service_host
    ):
        raise click.BadParameter(
            "You must specify both a name and a host for the state service"
        )


@app.resultcallback()
def run(processors, state_service_name, state_service_host, state_service_port, normalize_keys):
    state.configure(state_service_name, state_service_host, state_service_port)

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
