from nck.streams.json_stream import JSONStream
import dateutil.parser
from datetime import datetime


class FormatDateStream(JSONStream):
    keys = []
    date_format = '%Y-%m-%d'

    def __init__(self, name, source_generator, keys: [] = None, date_format: str = '%Y-%m-%d'):
        super().__init__(name, source_generator)
        FormatDateStream.keys = keys
        FormatDateStream.date_format = date_format

    @classmethod
    def encode_record(cls, record):
        return super().encode_record(cls._parse_record(record))

    @classmethod
    def _parse_record(self, o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in self.keys:
                    if len(v) > 1:
                        o[k] = self._format_date(v)
        return o

    @classmethod
    def _format_date(self, v):
        parsed_date = dateutil.parser.parse(v)
        datetimeobject = datetime.strptime(str(parsed_date), '%Y-%m-%d  %H:%M:%S')
        return datetimeobject.strftime(self.date_format)
