import click

from nck.commands.command import processor
from nck.readers.sql_reader import SQLReader, validate_sql_arguments
from nck.utils.args import extract_args


@click.command(name="read_mysql")
@click.option("--mysql-user", required=True)
@click.option("--mysql-password", required=True)
@click.option("--mysql-host", required=True)
@click.option("--mysql-port", required=False, default=3306)
@click.option("--mysql-database", required=True)
@click.option("--mysql-watermark-column")
@click.option("--mysql-watermark-init")
@click.option("--mysql-query")
@click.option("--mysql-query-name")
@click.option("--mysql-table")
@processor("mysql_password")
def mysql(**kwargs):
    validate_sql_arguments(MySQLReader, "mysql", kwargs)
    return MySQLReader(**extract_args("mysql_", kwargs))


class MySQLReader(SQLReader):
    @staticmethod
    def connector_adaptor():
        return "mysql+pymysql"
