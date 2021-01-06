# GNU Lesser General Public License v3.0 only
# Copyright (C) 2020 Artefact
# licence-information@artefact.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import click
import nck.helpers.api_client_helper as api_client_helper
from nck.clients.api_client import ApiClient
from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.streams.json_stream import JSONStream
from nck.utils.args import extract_args
import requests
from typing import Dict, Any, List
from nck.utils.secret_retriever import get_secret
from botocore.config import Config
import logging
import json
import boto3


@click.command(name="read_mytarget")
@click.option("--mytarget-client-id", required=True)
@click.option("--mytarget-client-secret", required=True)
@click.option("--mytarget-mail", required=True)
@click.option(
    "--mytarget-campaign-ids",
    "mytarget_campaign_ids",
    multiple=True
)
@processor("mytarget-client-id", "mytarget-client-secret")
def mytarget(**kwargs):
    return MyTargetReader(**extract_args("mytarget_", kwargs))


secret_keys = json.loads(get_secret('arn:aws:secretsmanager:eu-west-3:127773427021:secret:access-key-sanofi-ANrWKh', 'eu-west-3'))


s3_resource = boto3.resource(
    's3',
    aws_access_key_id=secret_keys.get('ACCESS_KEY'),
    aws_secret_access_key=secret_keys.get('SECRET_KEY'),
    region_name='eu-west-3',
    config=Config(
        retries={
            'max_attempts': 10
        }
    )
)


class MyTargetReader(Reader):

    def __init__(
        self,
        client_id,
        client_secret,
        mail,
        **kwargs
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.mail = mail
        self.campaign_ids = list(kwargs["campaign_ids"])
        self.access_token = None

    def create_token_request(self):
        url = 'https://target.my.com/api/v2/oauth2/token.json'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'target.my.com'
        }
        payload = dict(
            grant_type='client_credentials',
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        return dict(
            url=url,
            headers=headers,
            data=payload
        )

    def get_token_response(self):
        rsp = requests.post(**self.create_token_request())
        return rsp.json()

    def is_token_new(self, rsp):
        return "error" not in rsp.keys()

    def __write_file_s3(self, content: Dict[str, str]):
        s3_resource.Object('token-mytarget', 'last_token.json').put(Body=json.dumps(content))
        logging.info('The token has been uploaded to the bucket.')

    def __retrieve_token_file(self) -> Dict[str, str]:
        obj = s3_resource.Object('token-mytarget', 'last_token.json')
        logging.info('The last token has been retrieved from the bucket.')
        return json.loads(obj.get()['Body'].read())

    def retrieve_token(self):
        rsp = self.get_token_response()
        if self.is_token_new(rsp):
            logging.info("New token retrieved, going to store it to s3")
            self.__write_file_s3(rsp)
            return rsp
        else:
            logging.info("No more token available, going to retrieve the last one from s3")
            return self.__retrieve_token_file()

    def set_access_token(self, access_token):
        self.access_token = access_token

    def create_clients_list_request(self):
        url = 'https://target.my.com/api/v3/manager/clients.json'
        headers = {
            'Authorization': 'Bearer ' + self.access_token['access_token'],
            'Host': 'target.my.com'
        }
        payload = dict(
            grant_type='agency_client_credentials',
            client_id=self.client_id,
            client_secret=self.client_secret,
            agency_client_name=self.mail
        )
        return dict(
            url=url,
            headers=headers,
            data=payload
        )

    def retrieve_client_list(self):
        rsp = requests.get(**self.create_clients_list_request())
        return rsp.json()

    def get_list_clients(rsp: Dict[str, Any]) -> List[str]:
        return [
            element['user']['username']
            for element in rsp['items']
        ]

    def create_agency_token_request(self, agency_client):
        url = 'https://target.my.com/api/v2/oauth2/token.json'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'target.my.com'
        }
        payload = dict(
            grant_type='agency_client_credentials',
            client_id=self.client_id,
            client_secret=self.client_secret,
            agency_client_name=agency_client
        )
        return dict(
            url=url,
            headers=headers,
            data=payload
        )

    def retrieve_agency_tokens(self, list_agency_client):
        return [
            requests.post(**self.create_agency_token_request(agency_client)).json()
            for agency_client in list_agency_client
        ]

    def create_data_request_header(self):
        url = "https://target.my.com/api/v2/banners.json"
        headers = {
            'Authorization': 'Bearer ' + self.current_client_token['access_token'],
            'Host': 'target.my.com'
        }
        params = dict()
        return dict(
            url=url,
            headers=headers,
            data=params
        )

    def read(self):
        res = self.retrieve_token()
        self.set_access_token(res)
        print(self.access_token)
        res2 = self.retrieve_client_list()
        print(res2)
        yield JSONStream(
            "results_", res2
        )

    def create_refresh_request(self, token):
        '''
        this will return an access token with a different access_token but same refresh_token
        '''
        url = 'https://target.my.com/api/v2/oauth2/token.json'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'target.my.com'
        }
        payload = dict(
            grant_type='refresh_token',
            refresh_token=token['refresh_token'],
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        return dict(
            url=url,
            headers=headers,
            data=payload
        )

    def refresh_token(self, token):
        rsp = requests.post(**self.create_refresh_request(self.current_token))
        return rsp.json()['access_token']

    def set_refreshed_token(self, new_access_token):
        self.current_token['access_token'] = new_access_token

    def refresh_agency_token(self, client_token):
        rsp = requests.post(**self.create_refresh_request(client_token))
        return rsp.json()
