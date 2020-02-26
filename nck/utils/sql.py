# GNU Lesser General Public License v3.0 only
# Copyright (C) 2020 Artefact
# licence-information@artefact.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import sqlalchemy

_engine_meta = {}


def get_meta(engine, schema):
    global _engine_meta

    if engine not in _engine_meta:
        _engine_meta[engine] = sqlalchemy.MetaData(engine, schema=schema)

    return _engine_meta[engine]


def get_table(engine, schema, table):
    meta = get_meta(engine, schema)
    table = sqlalchemy.Table(table, meta, autoload=True, autoload_with=engine)

    return table


def build_table_query(engine, schema, table, watermark_column, watermark_value):
    if watermark_column and watermark_value:
        return build_table_query_with_watermark(
            engine, schema, table, watermark_column, watermark_value
        )
    else:
        return build_table_query_without_watermark(engine, schema, table)


def build_table_query_without_watermark(engine, schema, table):
    return get_table(engine, schema, table).select()


def build_table_query_with_watermark(
    engine, schema, table, watermark_column, watermark_value
):
    t = get_table(engine, schema, table)
    return t.select().where(t.columns[watermark_column] > watermark_value)


def build_custom_query(engine, query, watermark_column, watermark_value):
    statement = sqlalchemy.text(query)

    if watermark_column:
        params = {watermark_column: watermark_value}
        statement = statement.bindparams(**params)

    return statement
