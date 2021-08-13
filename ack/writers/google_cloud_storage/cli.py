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
from ack.utils.args import extract_args
from ack.utils.processor import processor
from ack.writers.google_cloud_storage.writer import GoogleCloudStorageWriter


@click.command(name="write_gcs")
@click.option("--gcs-bucket", help="GCS Bucket", required=True)
@click.option("--gcs-prefix", help="GCS path to write the file.")
@click.option("--gcs-project-id", help="GCS Project Id")
@click.option(
    "--gcs-file-name", help="Override the default name of the file (don't add the extension)",
)
@click.option("--gcs-file-format", "-f", help="File's format", default="njson", type=click.Choice(['njson', 'zstd']))
@processor()
def google_cloud_storage(**kwargs):
    return GoogleCloudStorageWriter(**extract_args("gcs_", kwargs))
