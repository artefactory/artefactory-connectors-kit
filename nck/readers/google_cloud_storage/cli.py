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
from nck.readers.google_cloud_storage.reader import GoogleCloudStorageReader
from nck.utils.args import extract_args
from nck.utils.processor import processor


@click.command(name="read_gcs")
@click.option("--gcs-bucket", required=True)
@click.option("--gcs-prefix", required=True, multiple=True)
@click.option("--gcs-format", required=True, type=click.Choice(["csv", "gz", "njson"]))
@click.option("--gcs-dest-key-split", default=-1, type=int)
@click.option("--gcs-csv-delimiter", default=",")
@click.option("--gcs-csv-fieldnames", default=None)
@processor()
def google_cloud_storage(**kwargs):
    return GoogleCloudStorageReader(**extract_args("gcs_", kwargs))
