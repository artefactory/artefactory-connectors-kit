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
from nck.config import logger

import click
import sqlalchemy
from nck.readers.reader import Reader
from nck.commands.command import processor
from nck.streams.json_stream import JSONStream
from nck.utils.args import extract_args, has_arg, hasnt_arg
from nck.utils.redis import RedisStateService
from nck.utils.retry import retry
from nck.utils.sql import build_custom_query, build_table_query


@click.command(name="read_mysql")
@click.option("--mysql-user", required=True)
@click.option("--mysql-password", required=True)
@click.option("--mysql-host", required=True)
@click.option("--mysql-port", default=3306)
@click.option("--mysql-database", required=True)
@click.option("--mysql-watermark-column")
@click.option("--mysql-watermark-init")
@click.option("--mysql-query")
@click.option("--mysql-query-name")
@click.option("--mysql-table")
@click.option("--mysql-redis-state-service-name")
@click.option("--mysql-redis-state-service-host")
@click.option("--mysql-redis-state-service-port", default=6379)
@processor("mysql_password")
def mysql(**kwargs):
    query_key = "mysql_query"
    query_name_key = "mysql_query_name"
    table_key = "mysql_table"
    watermark_column_key = "mysql_watermark_column"
    watermark_init_key = "mysql_watermark_init"
    redis_state_service_keys = [
        "mysql_redis_state_service_name",
        "mysql_redis_state_service_host",
        "mysql_redis_state_service_port",
    ]

    if hasnt_arg(query_key, kwargs) and hasnt_arg(table_key, kwargs):
        raise click.BadParameter("Must specify either a table or a query for MySQL reader")

    if has_arg(query_key, kwargs) and has_arg(table_key, kwargs):
        raise click.BadParameter("Cannot specify both a query and a table")

    if has_arg(query_key, kwargs) and hasnt_arg(query_name_key, kwargs):
        raise click.BadParameter("Must specify a query name when running a MySQL query")

    redis_state_service_enabled = all([has_arg(key, kwargs) for key in redis_state_service_keys])

    if has_arg(watermark_column_key, kwargs) and not redis_state_service_enabled:
        raise click.BadParameter("You must configure state management to use MySQL watermarks")

    if hasnt_arg(watermark_column_key, kwargs) and redis_state_service_enabled:
        raise click.BadParameter("You must specify a MySQL watermark when using state management")

    if hasnt_arg(watermark_init_key, kwargs) and redis_state_service_enabled:
        raise click.BadParameter("You must specify an initial MySQL watermark value when using state management")

    return MySQLReader(**extract_args("mysql_", kwargs))


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

        return JSONStream(self._name, result_generator())

    def close(self):
        logger.info("Closing MySQL connection")
        self._engine.dispose()
