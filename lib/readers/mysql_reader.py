import logging

import click

import pymysql
from lib.commands.command import processor
from lib.readers.reader import Reader
from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.utils.args import extract_args
from lib.utils.sql import select_all_from_table, Query
from lib.utils.retry import retry


@click.command(name="read_mysql")
@click.option("--mysql-user", required=True)
@click.option("--mysql-password", required=True)
@click.option("--mysql-host", required=True)
@click.option("--mysql-port", required=False, default=3306)
@click.option("--mysql-database", required=True)
@click.option("--mysql-query")
@click.option("--mysql-query-name")
@click.option("--mysql-table", multiple=True)
@processor
def mysql(**kwargs):

    if 'mysql_query' not in kwargs and 'mysql_table' not in kwargs:
        raise click.BadParameter("Must specify either a table or a query for MySQL reader")

    if 'mysql_query' in kwargs and kwargs['mysql_query_name'] is None:
        raise click.BadParameter("Must specify a query name when running a MySQL query")

    return MySQLReader(**extract_args('mysql_', kwargs))


class MySQLReader(Reader):

    _host = None
    _port = None
    _user = None
    _password = None
    _database = None

    _client = None

    def __init__(self, user, password, host, port, database, query=None, query_name=None, table=None):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database

        self._queries = self._build_table_queries(table)

        if query:
            self._queries.append(Query(name=query_name, query=query))

    @staticmethod
    def _build_table_queries(tables):
        _tables = tables or []
        return [select_all_from_table(table) for table in _tables]

    @retry
    def connect(self):
        logging.info("Connecting to MySQL Database {} on {}:{}".format(self._database, self._host, self._port))

        self._client = pymysql.connect(
            host=self._host,
            user=self._user,
            port=self._port,
            password=self._password,
            database=self._database,
            cursorclass=pymysql.cursors.DictCursor
        )

    def read(self):
        self.connect()

        try:
            for query in self._queries:
                yield self._run_query(query)
        finally:
            self.close()

    @retry
    def _run_query(self, query):
        logging.info("Running MySQL query %s", query)

        cursor = self._client.cursor()
        rows = cursor.execute(query.query)

        logging.info("MySQL result set contains %d rows", rows)

        def result_generator():
            row = cursor.fetchone()
            while row:
                yield row
                row = cursor.fetchone()
            cursor.close()

        return NormalizedJSONStream(query.name, result_generator())

    def close(self):
        logging.info("Closing MySQL connection")
        self._client.close()
