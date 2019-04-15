import datetime
import time
from config import logging

import click

import mysql.connector
from lib.commands.execute import app_default_options
from lib.readers.reader import BaseReader
from lib.streams.json_stream import JSONStream


@click.command(name="mysql")
@click.option("--mysql-host")
@click.option("--mysql-user")
@click.option("--mysql-password")
@click.option("--mysql-query")
@app_default_options
def mysql(**kwargs):
    return MySQLReader(
        kwargs.get("mysql_host"),
        kwargs.get("mysql_user"),
        kwargs.get("mysql_password"),
        kwargs.get("mysql_query")
    )


class MySQLReader(BaseReader):

    _stream = JSONStream

    _host = None
    _user = None
    _pass = None
    _database = None

    _client = None

    def __init__(self, host, user, password, database, query):
        logging.info("Instancing MYSQL Reader")
        self._host = host
        self._user = user
        self._pass = password
        self._database = database
        self._query = query

    def list(self):
        return [self._query]

    def connect(self):
        try:
            logging.info(
                "Connecting to MYSQL DB name {}".format(self._database))
            self._client = mysql.connector.connect(
                host=self._host,
                user=self._user,
                passwd=self._pass,
                database=self._database
            )
        except mysql.connector.Error as err:
            raise err

    def read(self, query):
        logging.info("Querying (%s)", query)
        try:
            cursor = self._client.cursor(dictionary=True)
            cursor.execute(self._query)
            results = cursor.fetchall()
            cursor.close()
        except mysql.connector.Error as err:
            raise err
        logging.info("Processing results")
        return self._database, results

    def close(self):
        logging.info("Closing MYSQL connection")
        self._client.close()
