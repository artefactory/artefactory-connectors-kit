import click
import config
import os
import logging
import httplib2

import datetime

from itertools import chain
from lib.commands.command import processor
from lib.readers.reader import Reader
from lib.utils.args import extract_args
from lib.utils.retry import retry
from lib.streams.json_stream import JSONStream


DISCOVERY_URI = "https://analyticsreporting.googleapis.com/$discovery/rest"

LIMIT_NVIEWS_PER_REQ = 5

ADOBE_API_ENDPOINT = "https://api.omniture.com/admin/1.4/rest/"

@click.command(name="read_adobe")
@click.option("--adobe-password", required=True)
@click.option("--adobe-username", required=True)
@click.option("--adobe-report-suite-id")
@click.option("--adobe-report-elements", type=click.Tuple([str, int]), multiple = True)
@click.option("--adobe-report-dimensions", type=click.Tuple([str, int]), multiple = True)
@click.option(
    "--adobe-day-range",
    type=click.Choice(["PREVIOUS_DAY", "LAST_30_DAYS", "LAST_7_DAYS", "LAST_90_DAYS"]),
    default=None,
)
@click.option("--adobe-date-range", nargs=2, type=click.DateTime())
@processor()
def adobe(**kwargs):
    # Should handle valid combinations dimensions/metrics in the API
    return AdobeReader(**extract_args("adobe_", kwargs))


class AdobeReader(Reader):
    def __init__(self,**kwargs):
      pass
