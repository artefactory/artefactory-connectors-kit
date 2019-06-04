from collections import namedtuple


Query = namedtuple('Query', ['name', 'query'])


def select_all_from_table(table):
    query = "SELECT * FROM {table}".format(table=table)
    return Query(name=table, query=query)



# def rdb_query_or_tables(query, tables):
#     return [query] if query else tables
#
#
# def rdb_table_name_from_query(query):
#     return query.split('FROM')[1].strip().split(' ')[0]
#
#
# def rdb_format_query(query_or_table):
#     if 'select' in query_or_table.lower():
#         return query_or_table
#     else:
#         return "SELECT * FROM {}".format(query_or_table)
#
#
# def rdb_format_column_name(column_name):
#     return column_name.strip().replace('-', '_').lower()
