import unittest
from lib.writers.gcs_writer import GCSWriter


class TestGCSWriter(unittest.TestCase):
    def test_extract_extension(self):
        filename = "test.py"
        print(GCSWriter._extract_extension(filename))
        assert GCSWriter._extract_extension(filename) == ("test", ".py")
