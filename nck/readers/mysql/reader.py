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

import sqlalchemy
from nck.config import logger
from nck.readers.reader import Reader
from nck.streams.normalized_json_stream import NormalizedJSONStream
from nck.utils.redis import RedisStateService
from nck.utils.retry import retry
from nck.readers.mysql.helper import build_custom_query, build_table_query


class MySQLReader(Reader):
    def __init__(
        self,
        user,
        password,
        host,
        port,
        database,
        watermark_column,
        watermark_init,
        query,
        query_name,
        table,
        schema,
        redis_state_service_name,
        redis_state_service_host,
        redis_state_service_port,
    ):

        self._engine = self._create_engine(host, port, user, password, database)
        self._name = table if table else query_name
        self._schema = schema
        self._watermark_column = watermark_column
        self._redis_state_service = RedisStateService(
            redis_state_service_name, redis_state_service_host, redis_state_service_port
        )

        if watermark_column:
            self._watermark_value = self._redis_state_service.get(self._name) or watermark_init

        if table:
            self._query = build_table_query(self._engine, schema, table, watermark_column, self._watermark_value)
        else:
            self._query = build_custom_query(self._engine, schema, query, watermark_column, self._watermark_value)

    @classmethod
    def _create_engine(cls, host, port, user, password, database):
        logger.info(f"Connecting to MySQL Database {database} on {host}:{port}")

        url = sqlalchemy.engine.url.URL(
            **{
                "drivername": "mysql+pymysql",
                "username": user,
                "password": password,
                "database": database,
                "port": port,
                "host": host,
            }
        )

        return sqlalchemy.create_engine(url)

    def read(self):
        try:
            yield self._run_query()
        finally:
            self.close()

    @retry
    def _run_query(self):
        logger.info(f"Running MySQL query {self._query}")

        rows = self._engine.execute(self._query)

        logger.info(f"MySQL result set contains {rows.rowcount} rows")

        def result_generator():
            row = rows.fetchone()
            while row:
                yield dict(row.items())

                if self._watermark_column:
                    self._redis_state_service.set(self._name, row[self._watermark_column])

                row = rows.fetchone()
            rows.close()

        return NormalizedJSONStream(self._name, result_generator())

    def close(self):
        logger.info("Closing MySQL connection")
        self._engine.dispose()
