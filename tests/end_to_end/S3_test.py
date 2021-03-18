import boto3
from moto import mock_s3
from unittest import TestCase

from nck.writers.amazon_s3.writer import AmazonS3Writer
from nck.readers.amazon_s3.reader import AmazonS3Reader

csv_file = [["a", "b", "c"], [4, 5, 6], [7, 8, 9]]


@mock_s3
class AmazonS3WriterTest(TestCase):
    @classmethod
    @mock_s3
    def setUpClass(cls):

        client = boto3.resource("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test")
        obj = client.Object("test", "filename.csv")
        obj.put(Body=b"some data")

    def test_Write(self):

        reader = AmazonS3Reader(
            bucket="test",
            bucket_region="us-east-1",
            access_key_id="",
            access_key_secret="",
            prefix=[""],
            format="csv",
            dest_key_split=-1,
            csv_delimiter=",",
            csv_fieldnames=None,
        )

        writer = AmazonS3Writer("test", "us-east-1", "", "", filename="ok")

        for stream in reader.read():
            writer.write(stream)

        client = boto3.resource("s3", region_name="us-east-1")
        bucket = client.Bucket("test")

        obj = list(bucket.objects.all())[-1]
        bod = obj.get()["Body"].read().decode("utf-8")
        self.assertEqual("some data", bod)
