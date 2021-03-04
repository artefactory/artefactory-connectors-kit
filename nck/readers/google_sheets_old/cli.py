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
from nck.commands.command import processor
from nck.readers.google_sheets_old.reader import GoogleSheetsReaderOld
from nck.utils.args import extract_args


@click.command(name="read_gsheets")
@click.option("--gsheets-url", required=True)
@click.option("--gsheets-worksheet-name", required=True, multiple=True)
@processor()
def google_sheets_old(**kwargs):
    return GoogleSheetsReaderOld(**extract_args("gsheets_", kwargs))
