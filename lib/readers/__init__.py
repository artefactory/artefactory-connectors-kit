from lib.readers.reader import Reader

from lib.readers.mysql_reader import mysql
# from lib.readers.oracle_reader import oracle
from lib.readers.gsheets_reader import gsheets
from lib.readers.salesforce_reader import salesforce


readers = [
    mysql,
    salesforce,
    gsheets
    # "oracle": oracle,
    # "gsheets": gsheets,
    # "salesforce": salesforce
]


__all__ = ['readers', 'Reader']
