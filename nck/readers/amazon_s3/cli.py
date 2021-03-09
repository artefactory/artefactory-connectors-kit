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
from nck.readers.amazon_s3.reader import AmazonS3Reader
from nck.utils.args import extract_args
from nck.utils.processor import processor


@click.command(name="read_s3")
@click.option("--s3-bucket", required=True)
@click.option("--s3-prefix", required=True, multiple=True)
@click.option("--s3-format", required=True, type=click.Choice(["csv", "gz", "njson"]))
@click.option("--s3-dest-key-split", default=-1, type=int)
@click.option("--s3-csv-delimiter", default=",")
@click.option("--s3-csv-fieldnames", default=None)
@processor()
def amazon_s3(**kwargs):
    return AmazonS3Reader(**extract_args("s3_", kwargs))
