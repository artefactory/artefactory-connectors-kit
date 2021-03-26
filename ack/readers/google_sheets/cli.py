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
from ack.readers.google_sheets.reader import GoogleSheetsReader
from ack.utils.args import extract_args
from ack.utils.processor import processor


@click.command(name="read_gs")
@click.option(
    "--gs-project-id",
    required=True,
    help="Project ID that is given by Google services once you have \
                  created your project in the google cloud console. You can retrieve it in the JSON credential file",
)
@click.option(
    "--gs-private-key-id",
    required=True,
    help="Private key ID given by Google services once you have added credentials \
                  to the project. You can retrieve it in the JSON credential file",
)
@click.option(
    "--gs-private-key",
    required=True,
    help="The private key given by Google services once you have added credentials \
                  to the project. \
                  You can retrieve it first in the JSON credential file",
)
@click.option(
    "--gs-client-email",
    required=True,
    help="Client e-mail given by Google services once you have added credentials \
                  to the project. You can retrieve it in the JSON credential file",
)
@click.option(
    "--gs-client-id",
    required=True,
    help="Client ID given by Google services once you have added credentials \
                  to the project. You can retrieve it in the JSON credential file",
)
@click.option(
    "--gs-client-cert",
    required=True,
    help="Client certificate given by Google services once you have added credentials \
                  to the project. You can retrieve it in the JSON credential file",
)
@click.option("--gs-sheet-key", required=True, help="Google spreadsheet key that is availbale in the url")
@click.option(
    "--gs-page-number",
    default=0,
    type=click.INT,
    help="The page number you want to access.\
    The number pages starts at 0",
)
@processor("gs_private_key_id", "gs_private_key", "gs_client_id", "gs_client_cert")
def google_sheets(**kwargs):
    return GoogleSheetsReader(**extract_args("gs_", kwargs))
