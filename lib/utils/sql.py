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


def select_all_from_table(table, watermark_column):
    if watermark_column:
        return select_all_from_table_with_watermark(table, watermark_column)
    else:
        return select_all_from_table_without_watermark(table)


def select_all_from_table_without_watermark(engine, table):
    return get_table(engine, table).select()


def select_all_from_table_with_watermark(engine, table, watermark_column):
    t = get_table(engine, table)

    raise NotImplementedError

    return t.select().where(t.columns[watermark_column])
