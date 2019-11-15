import logging
import sqlalchemy
import click


from lib.readers.reader import Reader
from lib.utils.sql import build_table_query, build_custom_query

from lib.utils.retry import retry

from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.state_service import state
from lib.utils.args import has_arg, hasnt_arg


def validate_sql_arguments(reader, prefix, kwargs):

    query_key = "{}_query".format(prefix)
    query_name_key = "{}_query_name".format(prefix)
    table_key = "{}_table".format(prefix)
    watermark_column_key = "{}_watermark_column".format(prefix)
    watermark_init_key = "{}_watermark_init".format(prefix)

    if hasnt_arg(query_key, kwargs) and hasnt_arg(table_key, kwargs):
        raise click.BadParameter("Must specify either a table or a query for {} reader".format(reader.connector_name()))

    if has_arg(query_key, kwargs) and has_arg(table_key, kwargs):
        raise click.BadParameter("Cannot specify both a query and a table")

    if has_arg(query_key, kwargs) and hasnt_arg(query_name_key, kwargs):
        raise click.BadParameter("Must specify a query name when running a {} query".format(reader.connector_name()))

    if has_arg(watermark_column_key, kwargs) and not state().enabled:
        raise click.BadParameter("You must activate state management to use {} watermarks".format(reader.connector_name()))

    if hasnt_arg(watermark_column_key, kwargs) and state().enabled:
        raise click.BadParameter("You must specify a {} watermark when using state management".format(reader.connector_name()))

    if hasnt_arg(watermark_init_key, kwargs) and state().enabled:
        raise click.BadParameter("You must specify a {} watermark init value when using state management".format(reader.connector_name()))


class SQLReader(Reader):

    _host = None
    _port = None
    _user = None
    _password = None
    _database = None
    _schema = None

    _client = None

    _watermark_value = None
    _watermark_column = None

    @classmethod
    def connector_name(cls):
        return cls.__name__

    def __init__(self, user, password, host, port, database,
                 watermark_column=None,
                 watermark_init=None,
                 query=None,
                 query_name=None,
                 table=None,
                 schema=None):

        self._engine = self._create_engine(host, port, user, password, database)
        self._name = table if table else query_name
        self._schema = schema

        self._watermark_column = watermark_column

        if watermark_column:
            self._watermark_value = self.state.get(self._name) or watermark_init

        if table:
            self._query = build_table_query(self._engine, schema, table, watermark_column, self._watermark_value)
        else:
            self._query = build_custom_query(self._engine, schema, query, watermark_column, self._watermark_value)

    @staticmethod
    def connector_adaptor():
        raise NotImplementedError

    @classmethod
    def _create_engine(cls, host, port, user, password, database):
        logging.info("Connecting to %s Database %s on %s:%s", cls.connector_name(), database, host, port)

        url = sqlalchemy.engine.url.URL(**{
            'drivername': cls.connector_adaptor(),
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
        logging.info("Running %s query %s", self.connector_name(), self._query)

        rows = self._engine.execute(self._query)

        logging.info("%s result set contains %d rows", self.connector_name(), rows.rowcount)

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
        logging.info("Closing %s connection", self.connector_name())
        self._engine.dispose()
