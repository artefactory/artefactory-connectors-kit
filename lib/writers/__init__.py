from lib.writers.writer import Writer

from lib.writers.gcs_writer import gcs
from lib.writers.console_writer import console
from lib.writers.local_writer import local
from lib.writers.bigquery_writer import bq
from lib.writers.s3_writer import s3


writers = [
    gcs,
    console,
    local,
    bq,
    s3
    # "oracle": oracle,
    # "gsheets": gsheets,
    # "salesforce": salesforce
]

__all__ = ['writers', 'Writer']
