from lib.readers.reader import Reader

from lib.readers.mysql_reader import mysql
from lib.readers.gcs_reader import gcs
from lib.readers.oracle_reader import oracle
from lib.readers.gsheets_reader import gsheets
from lib.readers.salesforce_reader import salesforce
from lib.readers.facebook_reader import facebook_marketing


readers = [
    mysql,
    salesforce,
    gsheets,
    gcs,
    facebook_marketing,
    oracle
]


__all__ = ['readers', 'Reader']
