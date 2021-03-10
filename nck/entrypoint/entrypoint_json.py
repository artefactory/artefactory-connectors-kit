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
import json
import sys
import click
import nck.entrypoint.entrypoint as entrypoint


@click.command()
@click.option(
    "--config-file", help="Path of the json file used to build the command.", required=True, type=click.Path(exists=True),
)
def add_json_args(config_file):
    with open(config_file) as f:
        data = json.load(f)

    del sys.argv[1:]
    sys.argv.extend(_parse_to_text(data))
    print(sys.argv)


def _parse_to_text(data):
    cmd_args = []
    readers = []
    writers = []
    for key, value in data.items():
        if key == "reader":
            readers.extend(_parse_reader_writer(value))
        elif key == "writers":
            for writer in value:
                writers.extend(_parse_reader_writer(writer))
        else:
            cmd_args.extend([key, value])

    return cmd_args + readers + writers


def _parse_reader_writer(data):
    res = [data.pop("name")]

    for key, value in data.items():
        res.extend([key, value])

    return res


if __name__ == "__main__":
    # we need to catch SystemExit as every Click command ends with this Exception
    try:
        add_json_args()
    except SystemExit as e:
        # to avoid to display the help text for entrypoint.py, we need to filter
        if "--help" not in sys.argv and e.code == 0:
            entrypoint.launch()
        pass
