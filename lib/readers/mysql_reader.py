import logging

import click

import sqlalchemy
from lib.commands.command import processor
from lib.readers.reader import Reader
from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.state_service import state
from lib.utils.args import extract_args
from lib.utils.sql import select_all_from_table, select_abitrary
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

    if 'mysql_query' not in kwargs and 'mysql_table' not in kwargs:
        raise click.BadParameter("Must specify either a table or a query for MySQL reader")

    if 'mysql_query' in kwargs and kwargs['mysql_query_name'] is None:
        raise click.BadParameter("Must specify a query name when running a MySQL query")

    if 'mysql_watermark_column' in kwargs and not state().enabled:
        raise click.BadParameter("You must activate state management to use MySQL watermarks")

    if 'mysql_watermark_column' not in kwargs and state().enabled:
        raise click.BadParameter("You must specify a MySQL watermark when using state management")

    return MySQLReader(**extract_args('mysql_', kwargs))


class MySQLReader(Reader):

    _host = None
    _port = None
    _user = None
    _password = None
    _database = None

    _client = None

    def __init__(self, user, password, host, port, database, watermark_column=None, query=None, query_name=None, table=None):
        self._engine = self._create_engine(host, port, user, password, database)
        self._watermark_column = watermark_column

        self._queries = []

        if table:
            self._queries.append((table, select_all_from_table(table, watermark_column)))

        if query:
            self._queries.append((query_name, select_abitrary(query, watermark_column)))

    @staticmethod
    def _create_engine(host, port, user, password, database):
        logging.info("Connecting to MySQL Database {} on {}:{}".format(database, host, port))

        url = sqlalchemy.URL(**{
            'drivername': 'mysql+pymsql',
            'username': user,
            'password': password,
            'database': database,
            'port': port,
            'host': host
        })

        return sqlalchemy.create_engine(url)

    def read(self):
        try:
            for query in self._queries:
                yield self._run_query(query)
        finally:
            self.close()

    @retry
    def _run_query(self, query):
        logging.info("Running MySQL query %s", query)

        name, q = query

        rows = self._engine.execute(q)

        logging.info("MySQL result set contains %d rows", rows.rowcount)

        def result_generator():
            row = rows.fetchone()
            while row:
                yield row
                row = rows.fetchone()
            rows.close()

        return NormalizedJSONStream(name, result_generator())

    def close(self):
        logging.info("Closing MySQL connection")
        self._engine.dispose()
