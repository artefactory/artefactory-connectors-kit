import logging

import click

import sqlalchemy
from lib.commands.command import processor
from lib.readers.reader import Reader
from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.state_service import state
from lib.utils.args import extract_args, has_arg, hasnt_arg
from lib.utils.sql import build_table_query, build_custom_query
from lib.utils.retry import retry


@click.command(name="read_mysql")
@click.option("--mysql-user", required=True)
@click.option("--mysql-password", required=True)
@click.option("--mysql-host", required=True)
@click.option("--mysql-port", required=False, default=3306)
@click.option("--mysql-database", required=True)
@click.option("--mysql-watermark-column")
@click.option("--mysql-query")
@click.option("--mysql-query-name")
@click.option("--mysql-table")
@processor
def mysql(**kwargs):

    if hasnt_arg('mysql_query', kwargs) and hasnt_arg('mysql_table', kwargs):
        raise click.BadParameter("Must specify either a table or a query for MySQL reader")

    if has_arg('mysql_query', kwargs) and has_arg('mysql_table', kwargs):
        raise click.BadParameter("Cannot specify both a query and a table")

    if has_arg('mysql_query', kwargs) and hasnt_arg('mysql_query_name', kwargs):
        raise click.BadParameter("Must specify a query name when running a MySQL query")

    if has_arg('mysql_watermark_column', kwargs) and not state().enabled:
        raise click.BadParameter("You must activate state management to use MySQL watermarks")

    if hasnt_arg('mysql_watermark_column', kwargs) and state().enabled:
        raise click.BadParameter("You must specify a MySQL watermark when using state management")

    return MySQLReader(**extract_args('mysql_', kwargs))


class MySQLReader(Reader):

    _host = None
    _port = None
    _user = None
    _password = None
    _database = None

    _client = None

    _watermark_value = None
    _watermark_column = None

    def __init__(self, user, password, host, port, database, watermark_column=None, query=None, query_name=None, table=None):
        self._engine = self._create_engine(host, port, user, password, database)
        self._name = table if table else query_name

        self._watermark_column = watermark_column

        if watermark_column:
            self._watermark_value = self.state.get(self._name)

        if table:
            self._query = build_table_query(self._engine, table, watermark_column, self._watermark_value)
        else:
            self._query = build_custom_query(self._engine, query, watermark_column, self._watermark_value)

    @staticmethod
    def _create_engine(host, port, user, password, database):
        logging.info("Connecting to MySQL Database {} on {}:{}".format(database, host, port))

        url = sqlalchemy.engine.url.URL(**{
            'drivername': 'mysql+pymysql',
            'username': user,
            'password': password,
            'database': database,
            'port': port,
            'host': host
        })

        return sqlalchemy.create_engine(url)

    def read(self):
        try:
            yield self._run_query()
        finally:
            self.close()

    @retry
    def _run_query(self):
        logging.info("Running MySQL query %s", self._query)

        rows = self._engine.execute(self._query)

        logging.info("MySQL result set contains %d rows", rows.rowcount)

        def result_generator():
            row = rows.fetchone()
            while row:
                yield dict(row.items())

                if self._watermark_column:
                    self.state.set(self._name, row[self._watermark_column])

                row = rows.fetchone()
            rows.close()

        return NormalizedJSONStream(self._name, result_generator())

    def close(self):
        logging.info("Closing MySQL connection")
        self._engine.dispose()
