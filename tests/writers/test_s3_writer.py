import boto3
import json

from moto import mock_s3
from unittest import TestCase
from parameterized import parameterized
from nck.writers.s3_writer import S3Writer
from nck.streams.json_stream import JSONStream


list_dict = [{"a": "4", "b": "5", "c": "6"}, {"a": "7", "b": "8", "c": "9"}]


def dict_generator(list_dict):
    for di in list_dict:
        yield di


def mock_stream(list_dict, name):
    return JSONStream(name, dict_generator(list_dict))


@mock_s3
class S3WriterTest(TestCase):
    @classmethod
    @mock_s3
    def setUpClass(cls):
        client1 = boto3.resource("s3", region_name="us-east-1")
        client1.create_bucket(Bucket="test")

    def test_bucket_doesnt_exist(self):
        with self.assertRaisesRegex(Exception, "non-existing-bucket bucket does not exist. available buckets are \['test'\]"):
            S3Writer("non-existing-bucket", "us-east-1", "", "")

    @parameterized.expand(
        [
            (None, "stream_name.format", "stream_name.format"),
            ("file_name", "stream_name.format", "file_name.format"),
        ]
    )
    def test_valid_filename(self, file_name, stream_name, expected):
        writer = S3Writer("test", "us-east-1", "", "", prefix=None, filename=file_name)
        writer._set_valid_file_name(stream_name)
        self.assertEqual(expected, writer._file_name)

    def test_Write(self):
        writer = S3Writer("test", "us-east-1", "", "")
        writer.write(mock_stream(list_dict, "test"))

        client = boto3.resource("s3", region_name="us-east-1")
        bucket = client.Bucket("test")

        obj = list(bucket.objects.all())[0]

        bod = obj.get()["Body"].read().decode("utf-8")
        lines = bod.split("\n")

        for i, line in enumerate(lines[:-1]):
            json_line = json.loads(line)
            self.assertEqual(json_line, list_dict[i])
