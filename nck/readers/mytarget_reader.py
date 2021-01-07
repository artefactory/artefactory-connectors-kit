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
from typing import Dict
from nck.utils.secret_retriever import get_secret
from botocore.config import Config
import logging
import json
import boto3
import itertools


@click.command(name="read_mytarget")
@click.option("--mytarget-client-id", required=True)
@click.option("--mytarget-client-secret", required=True)
@click.option("--mytarget-mail", required=True)
@click.option("--mytarget-agency", required=True)
@processor("mytarget-client-id", "mytarget-client-secret")
def mytarget(**kwargs):
    return MyTargetReader(**extract_args("mytarget_", kwargs))


secret_keys = json.loads(get_secret(
    'arn:aws:secretsmanager:eu-west-3:127773427021:secret:access-key-sanofi-ANrWKh',
    'eu-west-3')
)


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
        agency,
        **kwargs
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.mail = mail
        self.agency = agency
        self.access_token = None
        self.agency_client_token = None

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

    def retrieve_agency_client_response(self):
        return requests.post(**self.create_agency_token_request(self.agency)).json()

    def is_agency_client_token_new(self, rsp):
        return "error" not in rsp.keys()

    def __write_agency_client_token_s3(self, content: Dict[str, str]):
        s3_resource.Object('token-mytarget', f'{self.agency_client_token}_last_token.json').put(Body=json.dumps(content))
        logging.info('The token has been uploaded to the bucket.')

    def __retrieve_agency_client_token_file(self) -> Dict[str, str]:
        obj = s3_resource.Object('token-mytarget', f'{self.agency_client_token}_last_token.json')
        logging.info('The last token has been retrieved from the bucket.')
        return json.loads(obj.get()['Body'].read())

    def retrieve_agency_client_token(self):
        rsp = self.retrieve_agency_client_response()
        if self.is_agency_client_token_new(rsp):
            logging.info("New token retrieved, going to store it to s3")
            self.__write_agency_client_token_s3(rsp)
            return rsp
        else:
            logging.info("No more token available, going to retrieve the last one from s3")
            return self.__retrieve_agency_client_token_file()

    def set_agency_client_token(self):
        self.agency_client_token = self.retrieve_agency_client_token()

    def create_campaign_id_request(self, offset: int):
        url = "https://target.my.com/api/v2/banners.json"
        headers = {
            'Authorization': 'Bearer ' + self.agency_client_token['access_token'],
            'Host': 'target.my.com'
        }
        params = dict(offset=offset)
        return dict(
            url=url,
            headers=headers,
            params=params
        )

    def get_campaign_id_response(self, offset: int):
        return requests.get(**self.create_campaign_id_request(offset)).json()

    def get_all_campaign_id_ex(self):
        first_ids = self.get_campaign_id_response(0)
        count = first_ids['count']
        ids = [first_ids['items']]
        if count > 20:
            ids += [
                self.get_campaign_id_response(offset)['items']
                for offset in range(20, self.round_up_to_base(count, 20), 20)
            ]
        return list(itertools.chain.from_iterable(ids))

    def round_up_to_base(self, x, base):
        return base * round(x / base)

    def get_campaign_name_request(self, offset: int):
        url = "https://target.my.com/api/v2/campaigns.json"
        headers = {
            'Authorization': 'Bearer ' + self.agency_client_token['access_token'],
            'Host': 'target.my.com'
        }
        payload = dict(offset=offset)
        return dict(
            url=url,
            headers=headers,
            data=payload
        )

    def get_campaign_name_response(self, offset: int):
        return requests.get(**self.get_campaign_name_request(offset)).json()

    def get_all_campaign_names_ex(self):
        first_names = self.get_campaign_name_response(0)
        count = first_names['count']
        names = [first_names['items']]
        if count > 20:
            names += [
                self.get_campaign_name_response(offset)['items']
                for offset in range(20, self.round_up_to_base(count, 20), 20)
            ]
        res = list(itertools.chain.from_iterable(names))
        return res

    def get_banner_request(self, campaign_id, offset):
        url = "https://target.my.com/api/v2/banners.json"
        headers = {
            'Authorization': 'Bearer ' + self.agency_client_token['access_token'],
            'Host': 'target.my.com'
        }
        params = dict(_campaign_id=campaign_id, offset=offset)
        return dict(
            url=url,
            headers=headers,
            params=params
        )

    def get_banner_response(self, campaign_id, offset):
        return requests.get(**self.get_banner_request(campaign_id, offset)).json()

    def get_all_banners_one_camp(self, campaign_id):
        first_banners = self.get_banner_response(campaign_id, 0)
        count = first_banners['count']
        banners = [first_banners['items']]
        if count > 20:
            banners += [
                self.get_banner_response(campaign_id, offset)['items']
                for offset in range(20, self.round_up_to_base(count, 20), 20)
            ]
        all_banners = list(itertools.chain.from_iterable(banners))
        filtered_banners = [(x['id'], x['campaign_id']) for x in all_banners if x['moderation_status'] == 'allowed']
        return filtered_banners

    def get_all_banners_all_camp(self, campaign_ids):
        acc = []
        for campaign_id in campaign_ids:
            acc.extend(self.get_all_banners_one_camp(campaign_id))
        return dict(acc)

    def get_daily_banner_stat_request(self, banner_ids):
        url = "https://target.my.com/api/v2/statistics/banners/day.json"
        headers = {
            'Authorization': 'Bearer ' + self.agency_client_token['access_token'],
            'Host': 'target.my.com'
        }
        params = dict(
            id=banner_ids,
            date_from='2020-11-15',
            date_to='2020-12-06',
            metrics='all'
        )
        return dict(
            url=url,
            headers=headers,
            params=params
        )

    def get_daily_banner_stat_response(self, banner_ids):
        return requests.get(**self.get_daily_banner_stat_request(banner_ids)).json()

    def read(self):
        self.set_agency_client_token()
        rsp_id = self.get_all_campaign_id_ex()
        rsp_name = self.get_all_campaign_names_ex()

        campaign_ids = [element['campaign_id'] for element in rsp_id]
        rsp_banner = self.get_all_banners_all_camp(campaign_ids)
        rsp_daily_stat = self.get_daily_banner_stat_response(rsp_banner.keys())
        print(rsp_daily_stat)
        yield JSONStream(
            "results_" + rsp_daily_stat
        )
