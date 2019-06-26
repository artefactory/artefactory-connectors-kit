import json

from lib.streams.stream import Stream


class JSONStream(Stream):

    extension = "njson"
    mime_type = "application/json"

    @classmethod
    def decode_record(cls, record):
        return json.loads(record)

    @classmethod
    def encode_record(cls, record):
        return json.dumps(record, default=str)
