import click

from nck.commands.command import processor
from nck.readers.sql_reader import SQLReader, validate_sql_arguments
from nck.utils.args import extract_args


@click.command(name="read_oracle")
@click.option("--oracle-user", required=True)
@click.option("--oracle-password", required=True)
@click.option("--oracle-host", required=True)
@click.option("--oracle-port", required=False, default=2380)
@click.option("--oracle-database", required=True)
@click.option("--oracle-schema", required=True)
@click.option("--oracle-watermark-column")
@click.option("--oracle-watermark-init")
@click.option("--oracle-query")
@click.option("--oracle-query-name")
@click.option("--oracle-table")
@processor("oracle_password")
def oracle(**kwargs):
    validate_sql_arguments(OracleReader, "oracle", kwargs)
    return OracleReader(**extract_args("oracle_", kwargs))


class OracleReader(SQLReader):
    @staticmethod
    def connector_adaptor():
        return "oracle+cx_oracle"
