import datetime
import json
from config import logging

from lib.streams.temporaryfile_stream import TemporaryFileStream


class JSONStream(TemporaryFileStream):

    _extension = ".json"
    _mime_type = "application/json"
    _gcs_url = None

    def readline(self):
        for line in self._content:
            yield '{}\n'.format(json.dumps(self._format(line)))

    def _format(self, line):
        return {self._normalize_key(key): self._repr_str(line[key]) if line[key] is not None else "" for key in line}

    # TODO: Make this prettier, maybe remake it from scratch <3
    def _repr_str(self, val):
        try:
            if type(val) == int or type(val) == float:
                return repr(val).encode('utf-8')
            elif type(val) == datetime.datetime:
                return str(val)
            elif type(val) == dict:
                return self._format(val)
            else:
                return val.encode('utf-8')
        except UnicodeDecodeError as err:
            return val.decode('utf-8')

    def _normalize_key(self, key):
        return key.strip().replace(' ', '_')
