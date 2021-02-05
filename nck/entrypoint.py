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


@click.group(chain=True)
def cli():
    pass


def build_commands(cli, available_commands):
    for cmd in available_commands:
        cli.add_command(cmd)


@cli.resultcallback()
def process_command_pipeline(provided_commands):
    provided_readers = [cmd for cmd in provided_commands if isinstance(cmd(), Reader)]
    provided_writers = [cmd for cmd in provided_commands if isinstance(cmd(), Writer)]
    _validate_provided_commands(provided_readers, provided_writers)

    reader = provided_readers[0]
    for stream in reader().read():
        for writer in provided_writers:
            writer().write(stream)


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