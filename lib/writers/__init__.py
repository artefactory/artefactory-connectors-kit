from lib.writers.writer import Writer

from lib.writers.gcs_writer import gcs
from lib.writers.console_writer import console
from lib.writers.local_writer import local
from lib.writers.bigquery_writer import bq


writers = [
    gcs,
    console,
    local,
    bq
    # "oracle": oracle,
    # "gsheets": gsheets,
    # "salesforce": salesforce
]

__all__ = ['writers', 'Writer']
