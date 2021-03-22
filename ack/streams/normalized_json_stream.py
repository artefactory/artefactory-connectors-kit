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
from ack.streams.json_stream import JSONStream


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
        return (
            key.strip()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("(", "_")
            .replace(")", "")
            .replace(":", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace("][", "_")
            .replace("[", "_")
            .replace("]", "_")
            .replace(".", "_")
            .replace("%", "per")
            .strip("_")
        )
