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

import click
from ack.readers.mysql.reader import MySQLReader
from ack.utils.args import extract_args, has_arg, hasnt_arg
from ack.utils.processor import processor


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
