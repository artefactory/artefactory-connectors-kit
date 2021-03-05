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
import boto3
from nck.writers.objectstorage_writer import ObjectStorageWriter
from nck.commands.command import processor
from nck.utils.args import extract_args


@click.command(name="write_s3")
@click.option("--s3-bucket-name", help="S3 Bucket name", required=True)
@click.option("--s3-bucket-region", required=True)
@click.option("--s3-access-key-id", required=True)
@click.option("--s3-access-key-secret", required=True)
@click.option("--s3-prefix", help="s3 Prefix", default=None)
@click.option("--s3-filename", help="Override the default name of the file (don't add the extension)")
@processor("s3_access_key_id", "s3_access_key_secret")
def s3(**kwargs):
    return S3Writer(**extract_args("s3_", kwargs))


class S3Writer(ObjectStorageWriter):
    def __init__(self, bucket_name, bucket_region, access_key_id, access_key_secret, prefix=None, filename=None, **kwargs):
        self.boto_config = {
            "region_name": bucket_region,
            "aws_access_key_id": access_key_id,
            "aws_secret_access_key": access_key_secret,
        }
        super().__init__(bucket_name=bucket_name, prefix=prefix, file_name=filename, platform="S3", **kwargs)

    def _create_client(self):
        return boto3.resource("s3", **self.boto_config)

    def _create_bucket(self, client):
        return client.Bucket(self._bucket_name)

    def _list_buckets(self, client):
        return client.buckets.all()

    def _create_blob(self, file_name, stream):
        self._bucket.upload_fileobj(stream.as_file(), file_name)

    def _get_uri(self, file_name):
        return f"s3{self._get_file_path(file_name)}"
