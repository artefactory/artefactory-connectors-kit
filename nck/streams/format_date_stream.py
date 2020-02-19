# GNU Lesser General Public License v3.0 only
# Copyright (C) 2020 Artefact
# licence-information@artefact.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
from nck.streams.normalized_json_stream import NormalizedJSONStream
import dateutil.parser
from datetime import datetime


class FormatDateStream(NormalizedJSONStream):
    keys = []
    date_format = '%Y-%m-%d'

    def __init__(self, name, source_generator, keys: [] = None, date_format: str = '%Y-%m-%d'):
        super().__init__(name, source_generator)
        FormatDateStream.keys = keys
        FormatDateStream.date_format = date_format

    @classmethod
    def encode_record(cls, record):
        return super(FormatDateStream, cls).encode_record(cls._parse_record(record))

    @classmethod
    def _parse_record(cls, o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in cls.keys:
                    if len(v) > 1:
                        o[k] = cls._format_date(v)
        return o

    @classmethod
    def _format_date(cls, v):
        parsed_date = dateutil.parser.parse(v)
        datetimeobject = datetime.strptime(str(parsed_date), '%Y-%m-%d  %H:%M:%S')
        return datetimeobject.strftime(cls.date_format)
