import json

from lib.streams.stream import Stream


class JSONStream(Stream):
    extension = "njson"
    mime_type = "application/json"

    @classmethod
    def decode_record(cls, record):
        return json.loads(record, encoding="utf-8")

    @classmethod
    def encode_record(cls, record) -> str:
        return json.dumps(record, default=str)
