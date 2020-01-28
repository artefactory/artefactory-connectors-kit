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
