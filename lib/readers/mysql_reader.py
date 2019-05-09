import json
import os
from config import config, logging

import click
import mysql.connector as mysql_connector

from lib.commands.execute import app_default_options
from lib.readers.reader import BaseReader
from lib.streams.json_stream import JSONStream
from lib.utils.rdb_utils import (rdb_format_query, rdb_format_tables,
                                 rdb_query_or_tables,
                                 rdb_table_name_from_query)


@click.command(name="mysql")
@click.option("--mysql-credentials", required=True)
@click.option("--mysql-query")
@click.option("--mysql-tables")
@app_default_options
def mysql(**kwargs):
    credentials_path = os.path.join(config.get("SECRETS_PATH"), kwargs.get("mysql_credentials"))
    with open(credentials_path) as json_file:
        credentials_dict = json.loads(json_file.read())
        return MySQLReader(
            credentials_dict,
            query=kwargs.get("mysql_query"),
            tables=kwargs.get("mysql_tables")
        )


class MySQLReader(BaseReader):

    _stream = JSONStream

    _host = None
    _user = None
    _pass = None
    _database = None

    _client = None

    def __init__(self, credentials, query=None, tables=None):
        logging.info("Instancing MYSQL Reader")

        self._host = credentials.get("host")
        self._user = credentials.get("user")
        self._pass = credentials.get("password")
        self._database = credentials.get("database")

        self._query = query
        self._tables = rdb_format_tables(tables)

    def list(self):
        return rdb_query_or_tables(self._query, self._tables)

    def connect(self):
        try:
            logging.info(
                "Connecting to MYSQL DB name {}".format(self._database))
            self._client = mysql_connector.connect(
                host=self._host,
                user=self._user,
                passwd=self._pass,
                database=self._database
            )
        except mysql_connector.Error as err:
            raise err

    def read(self, query):
        logging.info("Querying (%s)", query)
        try:
            cursor = self._client.cursor(dictionary=True)
            formatted_query = rdb_format_query(query)
            cursor.execute(formatted_query)
            results = cursor.fetchall()
            cursor.close()
        except mysql_connector.Error as err:
            raise err
        logging.info("Processing results")
        return self._get_query_name(query), results

    def close(self):
        logging.info("Closing MYSQL connection")
        self._client.close()

    def _get_query_name(self, query_or_table):
        if self._tables:
            return query_or_table
        else:
            return rdb_table_name_from_query(query_or_table)
