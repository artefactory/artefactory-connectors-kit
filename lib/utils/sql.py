import sqlalchemy

_engine_meta = {}


def get_meta(engine):
    global _engine_meta

    if engine not in _engine_meta:
        _engine_meta[engine] = sqlalchemy.MetaData(engine)
        _engine_meta[engine].reflect()

    return _engine_meta[engine]


def get_table(engine, table):
    meta = get_meta(engine)

    if table not in meta.tables:
        raise Exception("Table does not exist")

    return meta.tables[table]


def build_table_query(engine, table, watermark_column,  watermark_value):
    if watermark_column and watermark_value:
        return build_table_query_with_watermark(engine, table, watermark_column, watermark_value)
    else:
        return build_table_query_without_watermark(engine, table)


def build_table_query_without_watermark(engine, table):
    return get_table(engine, table).select()


def build_table_query_with_watermark(engine, table, watermark_column, watermark_value):
    t = get_table(engine, table)
    return t.select().where(t.columns[watermark_column] > watermark_value)


def build_custom_query(engine, query, watermark_column,  watermark_value):
    statement = sqlalchemy.text(query)

    if watermark_column:
        params = {watermark_column: watermark_value}
        statement = statement.bindparams(**params)

    return statement
