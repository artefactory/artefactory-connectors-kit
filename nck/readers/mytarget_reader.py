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
from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.streams.json_stream import JSONStream
from nck.utils.args import extract_args
import requests
from typing import Dict, List, Any
import logging
import itertools
import time
from datetime import datetime


@click.command(name="read_mytarget")
@click.option("--mytarget-client-id", required=True)
@click.option("--mytarget-client-secret", required=True)
@click.option("--mytarget-mail", required=True)
@click.option("--mytarget-agency", required=True)
@click.option("--mytarget-refresh-token", required=True)
@click.option("--mytarget-start-date", type=click.DateTime())
@click.option("--mytarget-end-date", type=click.DateTime())
@click.option(
    "--mytarget-date-format",
    default="%Y-%m-%d",
    help="And optional date format for the output stream. "
    "Follow the syntax of https://docs.python.org/3.8/library/datetime.html#strftime-strptime-behavior",
)
@processor("mytarget-client-id", "mytarget-client-secret")
def mytarget(**kwargs):
    return MyTargetReader(**extract_args("mytarget_", kwargs))


class MyTargetReader(Reader):

    def __init__(
        self,
        client_id,
        client_secret,
        mail,
        agency,
        refresh_token,
        **kwargs
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.mail = mail
        self.agency = agency
        self.agency_client_token = {
            'access_token': None,
            'refresh_token': refresh_token
        }
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        self.date_format = kwargs.get('date_format')
        self.day_range = kwargs.get('day_range')

    def read(self):
        self.__check_date_input_validity()

        refreshed_token = self.get_refreshed_agency_token()
        self.set_agency_client_token(refreshed_token)

        response_id = self.get_all_campaign_ids()
        response_name = self.get_all_campaign_names()

        names_dict = self.convert_list_dicts_names_to_dict(response_name)
        ids_dict = self.convert_list_dicts_ids_to_dict(response_id)
        campaign_ids = [element['campaign_id'] for element in response_id]

        rsp_banner = self.get_all_banners_all_camp(campaign_ids)
        rsp_daily_stat = self.get_daily_banner_stat_response(rsp_banner.keys())
        rsp_banner_names = self.get_banner_name_response(list(rsp_banner))

        complete_daily_content = self.map_campaign_name_to_daily_stat(rsp_daily_stat, names_dict, ids_dict, rsp_banner_names)

        yield JSONStream(
            "results_", self.split_content_by_date(complete_daily_content)
        )

    def __check_date_input_validity(self) -> bool:
        """The goal of this function is to check the validity of the date input parameters before retrieving the data.
        """

        def __is_none(date: datetime) -> bool:
            return date is None

        def __check_validity_date(date: datetime) -> bool:
            try:
                datetime(date.year, date.month, date.day)
                logging.info(f'CORRECT: Date valid {date}')
                return True
            except ValueError as e:
                raise ValueError(f'The date is not valid : {e}')

        def __check_date_not_in_future(end_date: datetime) -> bool:
            if end_date <= datetime.now():
                logging.info(f'CORRECT: end date anterior or equal to current date {datetime.now()}')
                return True
            else:
                raise ValueError(f'The end date {end_date} is posterior to current date {datetime.now()}')

        def __check_both_start_end_valid_or_neither(
            start_date: datetime,
            end_date: datetime
        ) -> bool:
            if bool(__is_none(start_date)) ^ bool(__is_none(end_date)):
                raise ValueError("Either the start date or the end date is empty")
            else:
                logging.info('CORRECT: both dates are not empty')
                return True

        def __check_end_posterior_to_start(
            start_date: datetime,
            end_date: datetime
        ) -> bool:
            if start_date > end_date:
                raise ValueError(f"The start date {start_date} is posterior to end date {end_date}")
            else:
                logging.info('CORRECT: end date is equal or posterior to start date')
                return True

        return __check_both_start_end_valid_or_neither(self.start_date, self.end_date) and \
            __check_validity_date(self.start_date) & __check_validity_date(self.end_date) and \
            __check_end_posterior_to_start(self.start_date, self.end_date) and \
            __check_date_not_in_future(self.end_date)

    def __get_header(self, header_type: str):
        if header_type == "content_type":
            return {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'target.my.com'
            }
        elif header_type == "authorization":
            return {
                'Authorization': 'Bearer ' + self.agency_client_token['access_token'],
                'Host': 'target.my.com'
            }
        else:
            logging.error("No such kind of header available")

    def create_refresh_request(self):
        '''
        this will return an access token with a different access_token but same refresh_token
        '''
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.agency_client_token['refresh_token'],
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        return {
            'url': 'https://target.my.com/api/v2/oauth2/token.json',
            'headers': self.__get_header("content_type"),
            'data': payload
        }

    def get_refreshed_agency_token(self) -> Dict[str, str]:
        rsp = requests.post(**self.create_refresh_request())
        return rsp.json()

    def set_agency_client_token(self, agency_token):
        self.agency_client_token = agency_token

    def create_campaign_id_request(self, offset: int):
        params = {'offset': offset}
        return {
            'url': "https://target.my.com/api/v2/banners.json",
            'headers': self.__get_header("authorization"),
            'params': params
        }

    def get_campaign_id_response(self, offset: int):
        return requests.get(**self.create_campaign_id_request(offset)).json()

    def get_all_campaign_ids(self):
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
        params = {'offset': offset}
        return {
            'url': "https://target.my.com/api/v2/campaigns.json",
            'headers': self.__get_header("authorization"),
            'params': params
        }

    def get_campaign_name_response(
        self,
        offset: int
    ) -> List[Dict[str, str]]:
        return requests.get(**self.get_campaign_name_request(offset)).json()

    def convert_list_dicts_names_to_dict(
        self,
        list_dicts_names: List[Dict[str, str]]
    ) -> Dict[str, str]:
        new_dict = {}
        for dict_name_id in list_dicts_names:
            new_dict.update({dict_name_id['id'] : dict_name_id['name']})
        return new_dict

    def convert_list_dicts_ids_to_dict(
        self,
        list_dicts_ids: List[Dict[str, str]]
    ) -> Dict[str, str]:
        new_dict = {}
        for dict_ids in list_dicts_ids:
            new_dict.update({dict_ids['id'] : dict_ids['campaign_id']})
        return new_dict

    def get_all_campaign_names(self):
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
        params = {'_campaign_id': campaign_id, 'offset': offset}
        return {
            'url': "https://target.my.com/api/v2/banners.json",
            'headers': self.__get_header("authorization"),
            'params': params
        }

    def get_banner_response(
        self,
        campaign_id: str,
        offset: int
    ) -> List[Dict[str, str]]:
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
        filtered_banners = [(ban['id'], ban['campaign_id']) for ban in all_banners if ban['moderation_status'] == 'allowed']
        return filtered_banners

    def get_all_banners_all_camp(self, campaign_ids):
        acc = []
        for campaign_id in campaign_ids:
            acc.extend(self.get_all_banners_one_camp(campaign_id))
        return dict(acc)

    def get_daily_banner_stat_request(self, banner_ids):
        params = {
            'id': banner_ids,
            'date_from': '2021-01-01',
            'date_to': '2021-01-07',
            'metrics': 'all'
        }
        return {
            'url': "https://target.my.com/api/v2/statistics/banners/day.json",
            'headers': self.__get_header("authorization"),
            'params': params
        }

    def get_daily_banner_stat_response(
        self,
        banner_ids: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        return requests.get(**self.get_daily_banner_stat_request(banner_ids)).json()

    def get_banner_name_request(self, banner_id):
        params = {
            'date_from': '2021-01-01',
            'date_to': '2021-01-07',
            'metrics': 'all'
        }
        return {
            'url': f"https://target.my.com/api/v2/banners/{banner_id}.json?fields=id,name",
            'headers': self.__get_header("authorization"),
            'params': params
        }

    def get_banner_name_response(
        self,
        banner_ids: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        dict_ban_name = {}
        for ban_id in banner_ids:
            time.sleep(1)
            dict_ban_name[ban_id] = requests.get(**self.get_banner_name_request(ban_id)).json().get('name')
        return dict_ban_name

    def map_campaign_name_to_daily_stat(
        self,
        content: Dict[str, List[Dict[str, Any]]],
        names: List[Dict[str, str]],
        ids: Dict[str, str],
        banner_names: Dict[str, str]
    ) -> List[Dict[str, str]]:
        """Maps the campaign name to the daily statistics

        Args:
            content (Dict[str, Dict[str, Any]]): [description]
            names (List[Dict[str, str]]): [description]

        Returns:
            List[Dict[str, str]]: [description]
        """
        useful_content = content['items']
        for i in range(len(useful_content)):
            useful_content[i]['campaign_name'] = names[ids[useful_content[i]['id']]]
            useful_content[i]['campaign_id'] = ids[useful_content[i]['id']]
            useful_content[i]['banner_name'] = banner_names[useful_content[i]['id']]
        return useful_content

    def split_content_by_date(self, content):
        content_by_date = []
        dates = []
        for campaign_stats in content:
            new_line_base = {
                'campaign_id': campaign_stats['campaign_id'],
                'campaign_name': campaign_stats['campaign_name'],
                'banner_id': campaign_stats['id'],
                'banner_name': campaign_stats['banner_name']
            }
            for dict_daily_stats in campaign_stats['rows']:
                if dict_daily_stats['date'] not in dates:
                    dates.append(dict_daily_stats['date'])
                new_line = {**new_line_base, **dict_daily_stats}
                content_by_date.append(new_line)
        yield from content_by_date

    