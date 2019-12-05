import click
import config
import os
import logging
import httplib2
import datetime
import binascii
import uuid
import hashlib
import json

from itertools import chain
from lib.commands.command import processor
from lib.readers.reader import Reader
from lib.utils.args import extract_args
from lib.utils.retry import retry
from lib.streams.json_stream import JSONStream
import requests
from lib.helpers.adobe_helper import build_headers


DISCOVERY_URI = "https://analyticsreporting.googleapis.com/$discovery/rest"

LIMIT_NVIEWS_PER_REQ = 5

ADOBE_API_ENDPOINT = "https://api.omniture.com/admin/1.4/rest/"

@click.command(name="read_adobe")
@click.option("--adobe-password", required=True)
@click.option("--adobe-username", required=True)
@click.option("--adobe-list-report-suite")
@click.option("--adobe-report-suite-id")
@click.option("--adobe-report-element-id", multiple = True)
@click.option("--adobe-report-dimension-id", multiple = True)
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
    def __init__(self,password, username, **kwargs):
      self.password = password
      self.username = username
    
    @staticmethod
    def request(api, method, data=None):
        """ Compare with https://marketing.adobe.com/developer/api-explorer """
        api_method = '{0}.{1}'.format(api, method)
        data = data or dict()
        # logger.info("{}.{} {}".format(api, method, data))
        response = requests.post(
            ADOBE_API_ENDPOINT,
            params={'method': api_method},
            data=json.dumps(data),
            headers= build_headers(self.password, self.username)
        )
        json_response = response.json()
        #logger.debug("Response: {}".format(json_response))
        return json_response
    