import config
import logging
import os

import click
import boto3

from botocore.exceptions import ClientError

from lib.writers.writer import Writer
from lib.commands.command import processor
from lib.utils.args import extract_args
from lib.utils.retry import retry


@click.command(name="write_s3")
@click.option('--s3-bucket-name', help="S3 Bucket name", required=True)
@click.option('--s3-bucket-region', required=True, default = 'us-east-2')
@click.option('--s3-acess-key-id', required=True)
@click.option('--s3-access-key-secret', required=True)
@processor()
def s3(**kwargs):
    return S3Writer(**extract_args('s3_', kwargs))


class S3Writer(Writer):


    def __init__(self, bucket_name, acess_key_id, access_key_secret, bucket_region, **kwargs):
        boto_config = {
                       'region_name': bucket_region,
                       'aws_access_key_id': acess_key_id,
                       'aws_secret_access_key': access_key_secret
                       }
        self.bucket_name = bucket_name
        self.bucket_region = bucket_region
        self.s3_resource = boto3.resource('s3', **boto_config)
        self.s3_client = boto3.client('s3', **boto_config)

    @retry
    def write(self, stream):

        logging.info("Writing file to S3")
        bucket = self.s3_resource.Bucket(self.bucket_name) 

        if bucket in self.s3_resource.buckets.all():
            self.s3_resource.create_bucket(Bucket=self.bucket_name, CreateBucketConfiguration={'LocationConstraint': self.bucket_region})
        
        bucket.upload_fileobj(stream.as_file(), stream.name)
        url_file =  self.s3_client.generate_presigned_url('get_object', Params={'Bucket': self.bucket_name,'Key': stream.name}, ExpiresIn=3600)

        return url_file, bucket

        