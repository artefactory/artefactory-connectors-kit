from nck.streams.json_stream import JSONStream


class NormalizedJSONStream(JSONStream):
    @classmethod
    def encode_record(cls, record):
        return super(NormalizedJSONStream, cls).encode_record(cls._normalize_keys(record))

    @classmethod
    def _normalize_keys(cls, o):
        if isinstance(o, dict):
            return {cls._normalize_key(k): cls._normalize_keys(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [cls._normalize_keys(v) for v in o]
        elif o is None:
            return ""
        else:
            return o

    @staticmethod
    def _normalize_key(key):
        return key.strip().replace(" ", "_").replace("-", "_")
