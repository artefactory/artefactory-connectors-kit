from config import logging

import click
import requests

from lib.commands.execute import app_default_options
from lib.readers.reader import BaseReader
from lib.streams.json_stream import JSONStream


@click.command(name="api")
@click.option("--api-name")
@click.option("--api-user")
@click.option("--api-url")
@click.option("--api-endpoint")
@app_default_options
def api(**kwargs):
    return APIReader(
        kwargs.get("api_host"),
        kwargs.get("api_user"),
        kwargs.get("api_password"),
        kwargs.get("api_query")
    )


class APIReader(BaseReader):

    _stream = JSONStream

    def __init__(self, name, url, endpoint):
        self._name = name
        self._url = url
        self._endpoint = endpoint

    def list(self):
        return [self._endpoint]

    def connect(self):
        # implement OAUTH and BasicAuth
        pass

    def read(self, endpoint):
        endpoint_url = self.format_endpoint(endpoint)
        res = requests.get(endpoint_url)
        if res.status_code == 200:
            return self._name, res.json
        else:
            raise Exception("Requests goes wrong")

    def close(self):
        pass

    def format_endpoint(self, endpoint):
        return '{}/{}'.format(self._url, endpoint)
