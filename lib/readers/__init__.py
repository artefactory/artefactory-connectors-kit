from lib.readers.reader import Reader

from lib.readers.mysql_reader import mysql
from lib.readers.gcs_reader import gcs
from lib.readers.s3_reader import s3
from lib.readers.oracle_reader import oracle
from lib.readers.gsheets_reader import gsheets
from lib.readers.salesforce_reader import salesforce
from lib.readers.facebook_reader import facebook_marketing
from lib.readers.dbm_reader import dbm
from lib.readers.ga_reader import ga



readers = [
    mysql,
    salesforce,
    gsheets,
    gcs,
    s3,
    facebook_marketing,
    oracle,
    dbm,
    ga,
]


__all__ = ['readers', 'Reader']
