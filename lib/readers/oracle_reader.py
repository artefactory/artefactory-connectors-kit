
import datetime
import time
from config import logging

import click

import cx_Oracle
from lib.commands.execute import execute_builder, app_default_options
from lib.readers.reader import BaseReader
from lib.streams.json_stream import JSONStream


@click.command(name="oracle")
@click.option("--oracle-host")
@click.option("--oracle-port")
@click.option("--oracle-user")
@click.option("--oracle-password")
@click.option("--oracle-database")
@click.option("--oracle-query")
@app_default_options
def oracle(**kwargs):
    reader = OracleReader(
        kwargs.get("oracle_host"),
        kwargs.get("oracle_port"),
        kwargs.get("oracle_user"),
        kwargs.get("oracle_password"),
        kwargs.get("oracle_database"),
        kwargs.get("oracle_query")
    )
    execute_builder(reader, **kwargs)


class OracleReader(BaseReader):

    _stream = JSONStream

    _host = None
    _user = None
    _pass = None
    _database = None

    _client = None

    def __init__(self, host, port, user, password, database, query):
        logging.info("Instancing Oracle Reader")
        self._host = host
        self._user = user
        self._pass = password
        self._port = port
        self._database = database
        self._query = query

    def list(self):
        return [self._query]

    def connect(self):
        try:
            logging.info(
                "Connecting to Oracle DB name {}".format(self._database))
            connection_string = self.format_connection_string(
                self._user,
                self._pass,
                self.format_host(self._host, self._port, self._database)
            )
            logging.info("Connecting to {}".format(connection_string))
            self._client = cx_Oracle.connect(connection_string)
        except cx_Oracle.Error as err:
            raise err

    def read(self, query):
        logging.info("Querying (%s)", query)
        try:
            cursor = self._client.cursor()
            cursor.execute(self._query)
            results = self.format_results(cursor)
            cursor.close()
        except cx_Oracle.Error as err:
            raise err
        logging.info("Processing results")
        return self._database, results

    def format_results(self, cursor):
        """
            Transform results tuple as dict where keys are columns name
            attr:
                cursor (Oracle Cursor)
            returns:
                results (dict): keys are columns name and corresponding values
        """
        logging.info("Formatting results for stream")
        column_names = [d[0] for d in cursor.description]
        rows = list(cursor.fetchall())
        results = [dict(zip(column_names, row)) for row in rows]
        return results

    def format_host(self, host, port, db):
        host = '{}:{}/{}'.format(host, port, db)
        logging.info("Attempting to connect to {}".format(host))
        return host

    def format_connection_string(self, user, password, formatted_host):
        return '{}/{}@{}'.format(user, password, formatted_host)

    def close(self):
        logging.info("Closing Oracle connection")
        self._client.close()
