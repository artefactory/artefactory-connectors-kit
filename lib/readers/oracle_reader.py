# import json
# import os
# import logging
# import config
#
# import click
#
# import cx_Oracle
# from lib.commands.execute import app_default_options
# from lib.readers.reader import BaseReader
# from lib.streams.json_stream import JSONStream
# from lib.utils.rdb_utils import (rdb_format_column_name, rdb_format_query,
#                                  rdb_format_tables, rdb_query_or_tables,
#                                  rdb_table_name_from_query)
#
#
# @click.command(name="oracle")
# @click.option("--oracle-credentials", required=True)
# @click.option("--oracle-query")
# @click.option("--oracle-tables")
# @app_default_options
# def oracle(**kwargs):
#     credentials_path = os.path.join(config.get("SECRETS_PATH"), kwargs.get("oracle_credentials"))
#     with open(credentials_path) as json_file:
#         credentials_dict = json.loads(json_file.read())
#         return OracleReader(
#             credentials_dict,
#             kwargs.get("oracle_query"),
#             kwargs.get("oracle_tables")
#         )
#
#
# class OracleReader(BaseReader):
#
#     _stream = JSONStream
#
#     _host = None
#     _user = None
#     _pass = None
#     _database = None
#
#     _client = None
#
#     def __init__(self, credentials, query=None, tables=None):
#         logging.info("Instancing Oracle Reader")
#
#         self._host = credentials.get("host")
#         self._user = credentials.get("user")
#         self._pass = credentials.get("password")
#         self._port = credentials.get("port")
#         self._database = credentials.get("database")
#
#         self._query = query
#         self._tables = rdb_format_tables(tables)
#
#     def list(self):
#         return rdb_query_or_tables(self._query, self._tables)
#
#     def connect(self):
#         try:
#             logging.info(
#                 "Connecting to Oracle DB name {}".format(self._database))
#             connection_string = self.format_connection_string(
#                 self._user,
#                 self._pass,
#                 self.format_host(self._host, self._port, self._database)
#             )
#             self._client = cx_Oracle.connect(connection_string)
#         except cx_Oracle.Error as err:
#             raise err
#
#     def read(self, query):
#         try:
#             cursor = self._client.cursor()
#             formatted_query = rdb_format_query(query)
#             logging.info("Querying (%s)", query)
#             cursor.execute(formatted_query)
#             results = self.format_results(cursor)
#             cursor.close()
#         except cx_Oracle.Error as err:
#             raise err
#         logging.info("Processing results")
#         return self._get_query_name(query, results)
#
#     def format_results(self, cursor):
#         """
#             Transform results tuple as dict where keys are columns name
#             attr:
#                 cursor (Oracle Cursor)
#             returns:
#                 results (dict): keys are columns name and corresponding values
#         """
#         logging.info("Formatting results for stream")
#         column_names = [rdb_format_column_name(d[0]) for d in cursor.description]
#         rows = list(cursor.fetchall())
#         results = [dict(zip(column_names, row)) for row in rows]
#         return results
#
#     def format_host(self, host, port, db):
#         host = '{}:{}/{}'.format(host, port, db)
#         logging.info("Attempting to connect to {}".format(host))
#         return host
#
#     def format_connection_string(self, user, password, formatted_host):
#         return '{}/{}@{}'.format(user, password, formatted_host)
#
#     def close(self):
#         logging.info("Closing Oracle connection")
#         self._client.close()
#
#     def _get_query_name(self, query_or_table):
#         if self._tables:
#             return query_or_table
#         else:
#             return rdb_table_name_from_query(query_or_table)
