import pickle

from nck.streams.stream import Stream


class PickleStream(Stream):

    extension = "pickle"

    @classmethod
    def encode_record(cls, record):
        return pickle.dumps(record)

    @classmethod
    def decode_record(cls, record):
        return pickle.loads(record)
