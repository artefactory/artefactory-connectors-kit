import unittest
from nck.streams.format_date_stream import FormatDateStream
import json


class TestStreamBaseClassMethods(unittest.TestCase):
    data = """{"Date": "2020/01/27", "Impressions": "1286059"}
        {"Date": "2020/01/28", "Impressions": "889821"}
        {"Date": "2020/01/29", "Impressions": "1014673"}
        {"Date": "2020/01/30", "Impressions": "2119963"}
        {"Date": "2020/01/31", "Impressions": "1964449"}"""

    @staticmethod
    def data_generator(data):
        for elem in data.split('\n'):
            yield json.loads(elem)

    def test_usage(self):
        stream = FormatDateStream("result", self.data_generator(self.data), ["Date"])

        file = stream.as_file()
        buffer = "buf"
        res = b""
        while len(buffer) > 0:
            buffer = file.read(1024)
            res += buffer
        output = """{"Date": "2020-01-27", "Impressions": "1286059"}
                {"Date": "2020-01-28", "Impressions": "889821"}
                {"Date": "2020-01-29", "Impressions": "1014673"}
                {"Date": "2020-01-30", "Impressions": "2119963"}
                {"Date": "2020-01-31", "Impressions": "1964449"}
                """

        self.assertMultiLineEqual(res.decode().replace(" ", ""), output.replace(" ", ""))
