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

import collections

from ack.readers.reader import Reader
from ack.clients.salesforce.client import SalesforceClient
from ack.streams.json_stream import JSONStream
from ack.utils.redis import RedisStateService
from ack.utils.retry import retry


class SalesforceReader(Reader):
    def __init__(
        self,
        consumer_key,
        consumer_secret,
        user,
        password,
        query,
        query_name,
        object_type,
        watermark_column,
        watermark_init,
        redis_state_service_name,
        redis_state_service_host,
        redis_state_service_port,
    ):
        self._name = query_name or object_type
        self._client = SalesforceClient(user, password, consumer_key, consumer_secret)
        self._watermark_column = watermark_column
        self._watermark_init = watermark_init
        self._object_type = object_type
        self._query = query
        self._redis_state_service = RedisStateService(
            redis_state_service_name, redis_state_service_host, redis_state_service_port
        )

    def build_object_type_query(self, object_type, watermark_column):
        description = self._client.describe(object_type)
        fields = [f["name"] for f in description["fields"]]

        field_projection = ", ".join(fields)
        query = "SELECT {fields} FROM {object_type}".format(fields=field_projection, object_type=object_type)

        if watermark_column:
            query = "{base} WHERE {watermark_column} > {{{watermark_column}}}".format(
                base=query, watermark_column=watermark_column
            )

        return query

    @retry
    def read(self):
        def result_generator():

            watermark_value = None

            if self._watermark_column:
                watermark_value = self._redis_state_service.get(self._name) or self._watermark_init

            if self._object_type:
                self._query = self.build_object_type_query(self._object_type, self._watermark_column)

            if self._watermark_column:
                self._query = self._query.format(**{self._watermark_column: watermark_value})

            records = self._client.query(self._query)

            for rec in records:
                row = self._clean_record(rec)
                yield row

                if self._watermark_column:
                    self._redis_state_service.set(self._name, row[self._watermark_column])

        yield JSONStream(self._name, result_generator())

    @classmethod
    def _clean_record(cls, record):
        """
        Salesforces records contains metadata which we don't need during ingestion
        """
        return cls._flatten(cls._delete_metadata_from_record(record))

    @classmethod
    def _delete_metadata_from_record(cls, record):

        if isinstance(record, dict):
            strip_keys = ["attributes", "totalSize", "done"]
            return {k: cls._delete_metadata_from_record(v) for k, v in record.items() if k not in strip_keys}
        elif isinstance(record, list):
            return [cls._delete_metadata_from_record(i) for i in record]
        else:
            return record

    @classmethod
    def _flatten(cls, json_dict, parent_key="", sep="_"):
        """
        Reduce number of dict levels
        Note: useful to bigquery autodetect schema
        """
        items = []
        for k, v in json_dict.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(cls._flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
