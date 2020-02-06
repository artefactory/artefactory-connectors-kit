from nck.readers.reader import Reader

from nck.readers.mysql_reader import mysql
from nck.readers.gcs_reader import gcs
from nck.readers.googleads_reader import google_ads
from nck.readers.s3_reader import s3
from nck.readers.oracle_reader import oracle
from nck.readers.gsheets_reader import gsheets
from nck.readers.salesforce_reader import salesforce
from nck.readers.facebook_reader import facebook_marketing
from nck.readers.dbm_reader import dbm
from nck.readers.ga_reader import ga
from nck.readers.search_console_reader import search_console
from nck.readers.adobe_reader import adobe
from nck.readers.radarly_reader import radarly


readers = [
    mysql,
    salesforce,
    gsheets,
    gcs,
    google_ads,
    s3,
    facebook_marketing,
    oracle,
    dbm,
    ga,
    search_console,
    adobe,
    radarly,
]


__all__ = ["readers", "Reader"]
