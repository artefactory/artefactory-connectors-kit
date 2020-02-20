import unittest
import nck.entrypoint
from unittest import mock
from nck.streams.json_stream import JSONStream
from nck.streams.normalized_json_stream import NormalizedJSONStream

from nck.readers.reader import Reader
from nck.writers.writer import Writer
from click.testing import CliRunner


class Test_Normalize_Option(unittest.TestCase):
    runner = CliRunner()

    @staticmethod
    def mock_generator():
        for _ in range(3):
            yield {"plop plop": "plop"}

    @staticmethod
    def mock_read():
        yield JSONStream("plop", Test_Normalize_Option.mock_generator())

    @mock.patch.object(nck.readers.reader.Reader, 'read', mock_read)
    @mock.patch('nck.writers.writer.Writer.write')
    def test_normalize_behaviour(self, mock_write):
        r = Reader
        w = Writer
        nck.entrypoint.run([r, w], None, None, None, True)

        assert mock_write.call_args.args[0].__class__ == NormalizedJSONStream
