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
from nck.commands.command import processor
from nck.readers.sql_reader import SQLReader, validate_sql_arguments
from nck.utils.args import extract_args


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
    validate_sql_arguments(MySQLReader, "mysql", kwargs)
    return MySQLReader(**extract_args("mysql_", kwargs))


class MySQLReader(SQLReader):
    @staticmethod
    def connector_adaptor():
        return "mysql+pymysql"
