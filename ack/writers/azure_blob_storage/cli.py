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
import os

import click
from ack.utils.args import extract_args
from ack.utils.processor import processor
from ack.writers.azure_blob_storage.writer import AzureBlobStorageWriter


@click.command(name="write_azure_blob")
@click.option("--azure-blob-container", help="Azure container name", required=True)
@click.option(
    "--azure-blob-connection-string",
    default=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    help="Azure connection string, if not given it will try to get the environment variable 'AZURE_STORAGE_CONNECTION_STRING'",
)
@click.option("--azure-blob-prefix", help="Azure Prefix", default=None)
@click.option("--azure-blob-filename", help="Override the default name of the file (don't add the extension)")
@processor("azure_blob_connection_string")
def azure_blob_storage(**kwargs):
    return AzureBlobStorageWriter(**extract_args("azure_blob_", kwargs))
