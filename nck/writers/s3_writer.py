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
import logging
import click
import boto3
from nck.writers.writer import Writer
from nck.commands.command import processor
from nck.utils.args import extract_args
from nck.utils.retry import retry


@click.command(name="write_s3")
@click.option("--s3-bucket-name", help="S3 Bucket name", required=True)
@click.option("--s3-bucket-region", required=True)
@click.option("--s3-access-key-id", required=True)
@click.option("--s3-access-key-secret", required=True)
@click.option("--s3-prefix", help="s3 Prefix", default=None)
@click.option(
    "--s3-filename", help="Filename (without prefix). Be sure to add file extension."
)
@processor()
def s3(**kwargs):
    return S3Writer(**extract_args("s3_", kwargs))


class S3Writer(Writer):
    def __init__(
        self, bucket_name, access_key_id, access_key_secret, bucket_region, **kwargs
    ):
        boto_config = {
            "region_name": bucket_region,
            "aws_access_key_id": access_key_id,
            "aws_secret_access_key": access_key_secret,
        }
        self._bucket_name = bucket_name
        self._bucket_region = bucket_region
        self._s3_resource = boto3.resource("s3", **boto_config)
        self.kwargs = kwargs

    @retry
    def write(self, stream):

        logging.info("Writing file to S3")
        bucket = self._s3_resource.Bucket(self._bucket_name)

        if bucket not in self._s3_resource.buckets.all():
            self._s3_resource.create_bucket(
                Bucket=self._bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self._bucket_region},
            )

        bucket_region = self._s3_resource.meta.client.get_bucket_location(
            Bucket=self._bucket_name
        )["LocationConstraint"]

        # if the bucket region doesn't match the presigned url generated, will not work
        assert (
            bucket_region == self._bucket_region
        ), "the region you provided ({}) does'nt match the bucket's found region : ({}) ".format(
            self._bucket_region, bucket_region
        )
        if self.kwargs.get("prefix"):
            prefix = self.kwargs.get("prefix") + "/"
        else:
            prefix = ""

        filename = f"{prefix}{self.kwargs['filename'] if self.kwargs['filename'] is not None else stream.name}"
        bucket.upload_fileobj(stream.as_file(), filename)
        url_file = self._s3_resource.meta.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket_name, "Key": stream.name},
            ExpiresIn=3600,
        )

        return url_file, bucket
