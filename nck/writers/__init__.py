from nck.writers.writer import Writer

from nck.writers.gcs_writer import gcs
from nck.writers.console_writer import console
from nck.writers.local_writer import local
from nck.writers.bigquery_writer import bq
from nck.writers.s3_writer import s3


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
