def rdb_query_or_tables(query, tables):
    return [query] if query else tables


def rdb_format_tables(tables):
    return [table.strip() for table in tables.split(',')]


def rdb_table_name_from_query(query):
    return query.split('FROM')[1].strip().split(' ')[0]


def rdb_format_query(query_or_table):
    if 'select' in query_or_table.lower():
        return query_or_table
    else:
        return "SELECT * FROM {}".format(query_or_table)
