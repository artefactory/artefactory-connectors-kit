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


@click.command(name="read_oracle")
@click.option("--oracle-user", required=True)
@click.option("--oracle-password", required=True)
@click.option("--oracle-host", required=True)
@click.option("--oracle-port", default=2380)
@click.option("--oracle-database", required=True)
@click.option("--oracle-schema", required=True)
@click.option("--oracle-watermark-column")
@click.option("--oracle-watermark-init")
@click.option("--oracle-query")
@click.option("--oracle-query-name")
@click.option("--oracle-table")
@click.option("--oracle-redis-state-service-name")
@click.option("--oracle-redis-state-service-host")
@click.option("--oracle-redis-state-service-port", default=6379)
@processor("oracle_password")
def oracle(**kwargs):
    validate_sql_arguments(OracleReader, "oracle", kwargs)
    return OracleReader(**extract_args("oracle_", kwargs))


class OracleReader(SQLReader):
    @staticmethod
    def connector_adaptor():
        return "oracle+cx_oracle"
