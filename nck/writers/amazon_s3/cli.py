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
from nck.writers.amazon_s3.writer import AmazonS3Writer


@click.command(name="write_s3")
@click.option("--s3-bucket-name", help="S3 Bucket name", required=True)
@click.option("--s3-bucket-region", required=True)
@click.option("--s3-access-key-id", required=True)
@click.option("--s3-access-key-secret", required=True)
@click.option("--s3-prefix", help="s3 Prefix", default=None)
@click.option("--s3-filename", help="Filename (without prefix). Be sure to add file extension.")
@processor("s3_access_key_id", "s3_access_key_secret")
def amazon_s3(**kwargs):
    return AmazonS3Writer(**extract_args("s3_", kwargs))
