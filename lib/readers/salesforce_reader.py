import collections
import urllib

import logging

import click
import requests

from lib.readers.reader import Reader
from lib.commands.command import processor
from lib.state_service import state
from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.utils.args import extract_args, has_arg, hasnt_arg
from lib.utils.retry import retry

SALESFORCE_LOGIN_ENDPOINT = "https://login.salesforce.com/services/oauth2/token"
SALESFORCE_LOGIN_REDIRECT = "https://login.salesforce.com/services/oauth2/success"
SALESFORCE_SERVICE_ENDPOINT = "https://eu16.force.com"
SALESFORCE_QUERY_ENDPOINT = "/services/data/v42.0/query/"
SALESFORCE_DESCRIBE_ENDPOINT = "/services/data/v42.0/sobjects/{obj}/describe"


@click.command(name="read_salesforce")
@click.option("--salesforce-consumer-key", required=True)
@click.option("--salesforce-consumer-secret", required=True)
@click.option("--salesforce-user", required=True)
@click.option("--salesforce-password", required=True)
@click.option("--salesforce-object-type")
@click.option("--salesforce-query")
@click.option("--salesforce-query-name")
@click.option("--salesforce-watermark-column")
@click.option("--salesforce-watermark-init")
@processor("salesforce_consumer_key", "salesforce_consumer_secret", "salesforce_password")
def salesforce(**kwargs):
    query_key = 'salesforce_query'
    query_name_key = 'salesforce_query_name'
    object_type_key = 'salesforce_object_type'
    watermark_column_key = 'salesforce_watermark_column'
    watermark_init_key = 'salesforce_watermark_init'

    if hasnt_arg(query_key, kwargs) and hasnt_arg(object_type_key, kwargs):
        raise click.BadParameter("Must specify either an object type or a query for Salesforce")

    if has_arg(query_key, kwargs) and has_arg(object_type_key, kwargs):
        raise click.BadParameter("Cannot specify both a query and an object type for Salesforce")

    if has_arg(query_key, kwargs) and hasnt_arg(query_name_key, kwargs):
        raise click.BadParameter("Must specify a query name when running a Salesforce query")

    if has_arg(watermark_column_key, kwargs) and not state().enabled:
        raise click.BadParameter("You must activate state management to use Salesforce watermarks")

    if hasnt_arg(watermark_column_key, kwargs) and state().enabled:
        raise click.BadParameter("You must specify a Salesforce watermark when using state management")

    if hasnt_arg(watermark_init_key, kwargs) and state().enabled:
        raise click.BadParameter("You must specify an initial Salesforce watermark value when using state management")

    return SalesforceReader(**extract_args('salesforce_', kwargs))


class SalesforceClient(object):

    def __init__(self, user, password, consumer_key, consumer_secret):
        self._user = user
        self._password = password
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret

        self._headers = None
        self._access_token = None
        self._instance_url = None

    @property
    def headers(self):
        return {
            'Content-type': 'application/json',
            'Accept-Encoding': 'gzip',
            'Authorization': 'Bearer {}'.format(self.access_token)
        }

    @property
    def access_token(self):
        if not self._access_token:
            self._load_access_info()

        return self._access_token

    @property
    def instance_url(self):
        if not self._instance_url:
            self._load_access_info()

        return self._instance_url

    def _load_access_info(self):
        logging.info("Retrieving Salesforce access token")

        res = requests.post(SALESFORCE_LOGIN_ENDPOINT, params=self._get_login_params())

        res.raise_for_status()

        self._access_token = res.json().get("access_token")
        self._instance_url = res.json().get("instance_url")

        return self._access_token, self._instance_url

    def _get_login_params(self):
        return {
            "grant_type": "password",
            "client_id": self._consumer_key,
            "client_secret": self._consumer_secret,
            "username": self._user,
            "password": self._password,
            "redirect_uri": SALESFORCE_LOGIN_REDIRECT
        }

    def _request_data(self, path, params=None):

        endpoint = urllib.parse.urljoin(self.instance_url, path)
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def describe(self, object_type):
        path = SALESFORCE_DESCRIBE_ENDPOINT.format(obj=object_type)
        return self._request_data(path)

    def query(self, query):

        logging.info("Running Salesforce query: %s", query)

        response = self._request_data(SALESFORCE_QUERY_ENDPOINT, {'q': query})

        generating = True

        while generating:

            for rec in response['records']:
                yield rec

            if "nextRecordsUrl" in response:
                logging.info("Fetching next page of Salesforce results")
                response = self._request_data(response["nextRecordsUrl"])
            else:
                generating = False


class SalesforceReader(Reader):

    def __init__(self, consumer_key, consumer_secret, user, password, query, query_name, object_type, watermark_column,
                 watermark_init):
        self._name = query_name or object_type
        self._client = SalesforceClient(user, password, consumer_key, consumer_secret)
        self._watermark_column = watermark_column
        self._watermark_init = watermark_init
        self._object_type = object_type
        self._query = query

    def build_object_type_query(self, object_type, watermark_column):
        description = self._client.describe(object_type)
        fields = [f['name'] for f in description['fields']]

        field_projection = ", ".join(fields)
        query = "SELECT {fields} FROM {object_type}".format(fields=field_projection, object_type=object_type)

        if watermark_column:
            query = "{base} WHERE {watermark_column} > {{{watermark_column}}}".format(base=query,
                                                                                      watermark_column=watermark_column)

        return query

    @retry
    def read(self):

        def result_generator():

            watermark_value = None

            if self._watermark_column:
                watermark_value = self.state.get(self._name) or self._watermark_init

            if self._object_type:
                self._query = self.build_object_type_query(self._object_type, self._watermark_column)

            if self._watermark_column:
                self._query = self._query.format(**{self._watermark_column: watermark_value})

            records = self._client.query(self._query)

            for rec in records:
                row = self._clean_record(rec)
                yield row

                if self._watermark_column:
                    self.state.set(self._name, row[self._watermark_column])

        yield NormalizedJSONStream(self._name, result_generator())

    @classmethod
    def _clean_record(cls, record):
        """
            Salesforces records contains metadata which we don't need during ingestion
        """
        return cls._flatten(cls._delete_metadata_from_record(record))

    @classmethod
    def _delete_metadata_from_record(cls, record):

        if isinstance(record, dict):
            strip_keys = ["attributes", "totalSize", "done"]
            return {k: cls._delete_metadata_from_record(v) for k, v in record.items() if k not in strip_keys}
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
