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
from nck.utils.args import extract_args
from nck.utils.processor import processor
from nck.writers.local.writer import LocalWriter


@click.command(name="write_local")
@click.option("--local-directory", "-d", required=True, help="Destination directory")
@click.option("--local-file-name", "-n", help="Destination file name")
@processor()
def local(**kwargs):
    return LocalWriter(**extract_args("local_", kwargs))
