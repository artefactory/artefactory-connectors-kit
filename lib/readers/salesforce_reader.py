import collections
import urlparse

import logging

import click
import requests

from lib.readers.reader import Reader
from lib.commands.command import processor
from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.utils.args import extract_args
from lib.utils.retry import retry


SALESFORCE_LOGIN_ENDPOINT = "https://login.salesforce.com/services/oauth2/token"
SALESFORCE_LOGIN_REDIRECT = "https://login.salesforce.com/services/oauth2/success"
SALESFORCE_SERVICE_ENDPOINT = "https://eu16.force.com"
SALESFORCE_QUERY_ENDPOINT = "/services/data/v42.0/query/"


@click.command(name="read_salesforce")
@click.option("--salesforce-name", required=True)
@click.option("--salesforce-consumer-key", required=True)
@click.option("--salesforce-consumer-secret", required=True)
@click.option("--salesforce-user", required=True)
@click.option("--salesforce-password", required=True)
@click.option("--salesforce-query", required=True)
@processor
def salesforce(**kwargs):
    return SalesforceReader(**extract_args('salesforce_', kwargs))


class SalesforceReader(Reader):

    def __init__(self, name, consumer_key, consumer_secret, user, password, query):
        self._name = name
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._user = user
        self._password = password
        self._query = query

    @retry
    def read(self):
        access_token, instance_url = self._get_access_token()
        headers = self._get_headers(access_token)
        endpoint = urlparse.urljoin(instance_url, SALESFORCE_QUERY_ENDPOINT)

        def result_generator(endpoint):
            response = self._request_data(endpoint, headers, {'q': self._query})
            generating = True

            while generating:
                for rec in response['records']:
                    yield self._clean_record(rec)

                if "nextRecordsUrl" in response:

                    logging.info("Fetching next page of Salesforce results")

                    endpoint = urlparse.urljoin(instance_url, response["nextRecordsUrl"])
                    response = self._request_data(endpoint, headers)
                else:
                    generating = False

        yield NormalizedJSONStream(self._name, result_generator(endpoint))

    def _get_login_params(self):
        return {
            "grant_type": "password",
            "client_id": self._consumer_key,
            "client_secret": self._consumer_secret,
            "username": self._user,
            "password": self._password,
            "redirect_uri": SALESFORCE_LOGIN_REDIRECT
        }

    def _get_headers(self, access_token):
        return {
            'Content-type': 'application/json',
            'Accept-Encoding': 'gzip',
            'Authorization': 'Bearer {}'.format(access_token)
        }

    def _get_access_token(self):

        logging.info("Retrieving Salesforce access token")

        res = requests.post(SALESFORCE_LOGIN_ENDPOINT, params=self._get_login_params())
        access_token = res.json().get("access_token")
        instance_url = res.json().get("instance_url")

        return access_token, instance_url

    @classmethod
    def _clean_record(cls, record):
        """
            Salesforces records contains metadata which we don't need in ingestion
        """
        return cls._flatten(cls._delete_metadata_from_record(record))

    @classmethod
    def _delete_metadata_from_record(cls, record):

        if isinstance(record, dict):
            strip_keys = ["attributes", "totalSize", "done"]
            return {k: cls._delete_metadata_from_record(v) for k, v in record.iteritems() if k not in strip_keys}
        elif isinstance(record, list):
            return [cls._delete_metadata_from_record(i) for i in record]
        else:
            return record

    @classmethod
    def _flatten(cls, json_dict, parent_key="", sep="_"):
        """
        Reduce number of dict levels
        Note: useful to bigquery autodetect schema
        """
        items = []
        for k, v in json_dict.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(cls._flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _request_data(self, endpoint, headers, params=None):
        response = requests.get(
            endpoint,
            headers=headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()
