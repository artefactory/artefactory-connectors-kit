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
import requests
from typing import Dict, List, Any, Tuple
import logging
import itertools
import time
from datetime import datetime
from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.streams.json_stream import JSONStream
from nck.utils.args import extract_args
from nck.helpers.mytarget_helper import REQUEST_CONFIG


@click.command(name="read_mytarget")
@click.option("--mytarget-client-id", required=True)
@click.option("--mytarget-client-secret", required=True)
@click.option("--mytarget-mail", required=True)
@click.option("--mytarget-agency", required=True)
@click.option("--mytarget-refresh-token", required=True)
@click.option("--mytarget-start-date", type=click.DateTime(), required=True)
@click.option("--mytarget-end-date", type=click.DateTime(), required=True)
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
        self.agency_client_token = {'refresh_token': refresh_token}
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        self.date_format = kwargs.get('date_format')
        self.day_range = kwargs.get('day_range')

    def read(self):
        self.__check_date_input_validity()
        self.__retrieve_and_set_token()

        rsp_daily_stat, names_dict, ids_dict, rsp_banner_names = self.__retrieve_all_data()

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
                return True
            except ValueError as e:
                raise ValueError(f'The date is not valid : {e}')

        def __check_date_not_in_future(end_date: datetime) -> bool:
            if end_date <= datetime.now():
                return True
            else:
                raise ValueError(f'The end date {end_date} is posterior to current date {datetime.now()}')

        def __check_both_start_end_valid_or_neither(
            start_date: datetime,
            end_date: datetime
        ) -> bool:
            if __is_none(start_date) or __is_none(end_date):
                raise ValueError("Either the start date or the end date is empty")
            else:
                return True

        def __check_end_posterior_to_start(
            start_date: datetime,
            end_date: datetime
        ) -> bool:
            if start_date > end_date:
                raise ValueError(f"The start date {start_date} is posterior to end date {end_date}")
            else:
                return True

        return __check_both_start_end_valid_or_neither(self.start_date, self.end_date) and \
            __check_validity_date(self.start_date) & __check_validity_date(self.end_date) and \
            __check_end_posterior_to_start(self.start_date, self.end_date) and \
            __check_date_not_in_future(self.end_date)

    def __retrieve_and_set_token(self):
        parameters_refresh_token = self.__generate_params_dict('refresh_agency_token')
        request_refresh_token = self.__create_request('refresh_agency_token', parameters_refresh_token)
        refreshed_token = requests.post(**request_refresh_token).json()
        self.set_agency_client_token(refreshed_token)

    def __retrieve_all_data(
        self) -> Tuple(
            Dict[str, List[Dict[str, Any]]],
            List[Dict[str, str]],
            Dict[str, str],
            Dict[str, str]):
        response_id = self.__get_all_results('get_campaign_ids')
        response_name = self.__get_all_results('get_campaign_names')

        names_dict = self.convert_list_dicts_to_dict(response_name, 'name')
        ids_dict = self.convert_list_dicts_to_dict(response_id, 'campaign_id')

        campaign_ids = [element['campaign_id'] for element in response_id]
        rsp_banner = self.get_all_banners_all_camp(campaign_ids)

        rsp_daily_stat = self.__get_response('get_banner_stats', banner_ids=rsp_banner.keys())
        rsp_banner_names = self.get_banner_name_response('get_banner_names', list(rsp_banner))

        return rsp_daily_stat, names_dict, ids_dict, rsp_banner_names

    def __get_all_results(
        self,
        name_content: str,
        offset=0,
        campaign_id=0,
        banner_ids=[]
    ) -> List[Dict[str, str]]:
        """Based on the __get_response function this function is incrementing through offsets according to the
        number of elements given by the first response.

        Args:
            name_content (str): string representing key of parameters config dict
            offset (int, optional): potential offset of the request. Defaults to 0.
            campaign_id (int, optional): potential campaign id of the request. Defaults to 0.
            banner_ids (list, optional): potential banner ids list of the request. Defaults to [].

        Returns:
            List[Dict[str, Any]]: list of dicts resulting from the requests we made to the api
        """
        first_elements = self.__get_response(name_content, campaign_id=campaign_id, banner_ids=banner_ids)
        count = first_elements['count']
        elements = [first_elements['items']]
        if count > 20:
            elements += [
                self.__get_response(name_content, offset=offset, campaign_id=campaign_id, banner_ids=banner_ids)['items']
                for offset in range(20, self.round_up_to_base(count, 20), 20)
            ]
        return list(itertools.chain.from_iterable(elements))

    def get_all_banners_all_camp(self, campaign_ids, banner_ids=[]):
        all_banner = []
        for campaign_id in campaign_ids:
            all_banner.extend(self.get_all_banners_one_camp(campaign_id, banner_ids=banner_ids))
        return dict(all_banner)

    def get_all_banners_one_camp(self, campaign_id, banner_ids=[]):
        all_banners = self.__get_all_results('get_banner_ids', campaign_id=campaign_id, banner_ids=banner_ids)
        filtered_banners = [(ban['id'], ban['campaign_id']) for ban in all_banners if ban['moderation_status'] == 'allowed']
        return filtered_banners

    def get_banner_name_response(
        self,
        name_content: str,
        banner_ids: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """This function is querying the API to retrieve the name linked to a banner id.
        We neeed to add sleep time as too frequent queries lead to error results.

        Args:
            name_content (str): string indicating the parameters to retrieve from config dict
            banner_ids (Dict[str, str]): ids which need to be linked to a name

        Returns:
            List[Dict[str, Any]]: list of dict containing the id and name.
        """
        dict_ban_name = {}
        for ban_id in banner_ids:
            time.sleep(1)
            dict_ban_name[ban_id] = self.__get_response(name_content, specific_ban_id=ban_id).get('name')
        return dict_ban_name

    def map_campaign_name_to_daily_stat(
        self,
        daily_stats: Dict[str, List[Dict[str, Any]]],
        names: List[Dict[str, str]],
        ids: Dict[str, str],
        banner_names: Dict[str, str]
    ) -> List[Dict[str, str]]:
        useful_content = daily_stats['items']
        for i in range(len(useful_content)):
            useful_content[i]['campaign_name'] = names[ids[useful_content[i]['id']]]
            useful_content[i]['campaign_id'] = ids[useful_content[i]['id']]
            useful_content[i]['banner_name'] = banner_names[useful_content[i]['id']]
        return useful_content

    def split_content_by_date(self, content: List[Dict[str, Any]]):
        """The goal of this function is to create a line for each date from the date range
        for each banner/campaign association. This will be retrieved by the JSON reader thanks
        to the yield from.

        Args:
            content (List[Dict[str, Any]]): List of the dicts containing all the informations

        Yields:
            [type]: the result will be retrieved line by line by the reader.
        """
        content_by_date = []
        dates = []
        for campaign_stats in content:
            new_line_base = {
                'campaign_id': campaign_stats['campaign_id'],
                'campaign_name': campaign_stats['campaign_name'],
                'banner_id': campaign_stats['id'],
                'banner_name': campaign_stats.get('banner_name')
            }
            for dict_daily_stats in campaign_stats['rows']:
                if dict_daily_stats['date'] not in dates:
                    dates.append(dict_daily_stats['date'])
                new_line = {**new_line_base, **dict_daily_stats}
                content_by_date.append(new_line)
        yield from content_by_date

    def __get_response(
        self,
        name_content: str,
        offset=0,
        campaign_id=0,
        banner_ids=[],
        specific_ban_id=0
    ) -> Dict[str, Any]:
        """This function makes a request to the api after building eveything necessary to get the
        desired results for a specific need which is defined by name_content.

        Args:
            name_content (str): string representing key of parameters config dict
            offset (int, optional): potential offset of the request. Defaults to 0.
            campaign_id (int, optional): potential campaign id of the request. Defaults to 0.
            banner_ids (list, optional): potential banner ids list of the request. Defaults to [].
            specific_ban_id (int, optional): id to parse to the url. Defaults to 0.

        Returns:
            Dict[str, Any]: dict resulting from the request we made to the api
        """
        parameters = self.__generate_params_dict(name_content, offset=offset, campaign_id=campaign_id, banner_ids=banner_ids)
        request = self.__create_request(name_content, parameters, specific_ban_id=specific_ban_id)
        return requests.get(**request).json()

    def __create_request(
        self,
        name_content: str,
        parameters: Dict[str, Any],
        specific_ban_id=0
    ) -> Dict[str, Any]:
        """This function creates the dict with all the parameters required to query the api

        Args:
            name_content (str): string representing key of parameters config dict
            parameters (Dict[str, Any]): dict of parameters retrieved from get_params_dict
            specific_ban_id (int, optional): id to build the url if required. Defaults to 0.

        Returns:
            Dict[str, Any]: dict used to make a request to the api
        """
        req_base = {
            'url': self.__get_url(name_content, specific_ban_id=specific_ban_id),
            'headers': self.__get_header(REQUEST_CONFIG[name_content]['headers_type'])
        }
        return {**req_base, **parameters}

    def __get_url(
        self,
        name_content: str,
        specific_ban_id=0
    ) -> str:
        """This function retrieves the url and if it is mandatory to add an id in the url
        we fill if using substitute.

        Args:
            name_content (str): string representing key of parameters config dict
            specific_ban_id (int, optional): id to parse to the url. Defaults to 0.

        Returns:
            str: url endpoint
        """
        url = REQUEST_CONFIG[name_content]['url']
        if name_content == 'get_banner_names':
            url = url.substitute(id=specific_ban_id)
        return url

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

    def __generate_params_dict(
        self,
        name_content: str,
        offset=0,
        campaign_id=0,
        banner_ids=[]
    ) -> Dict[str, Any]:
        """This function returns a dict containing all the parameters required
        for the request.

        Args:
            name_content (str): string representing key of parameters config dict
            offset (int, optional): potential offset of the request. Defaults to 0.
            campaign_id (int, optional): potential campaign id of the request. Defaults to 0.
            banner_ids (list, optional): potential banner ids list of the request. Defaults to [].

        Returns:
            Dict[str, Any]: params to give to the request dict
        """
        dict_config = REQUEST_CONFIG[name_content]
        params = {}
        if name_content == 'refresh_agency_token' :
            params['data'] = {
                'grant_type': 'refresh_token',
                'refresh_token': self.agency_client_token['refresh_token'],
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
        else:
            params['params'] = {}
            if dict_config['offset']:
                params['params']['offset'] = offset
            if dict_config['_campaign_id']:
                params['params']['_campaign_id'] = campaign_id
            if dict_config['dates_required']:
                params['params'] = {
                    'date_from': self.start_date.strftime('%Y-%m-%d'),
                    'date_to': self.end_date.strftime('%Y-%m-%d'),
                    'metrics': 'all'
                }
            if dict_config['ids']:
                params['params']['id'] = banner_ids
        return params

    def convert_list_dicts_to_dict(
        self,
        list_dicts: List[Dict[str, str]],
        field_name: str
    ) -> Dict[str, str]:
        """Transformss a list of dicts to a dict containing all the ids and the content retrieved from the
        field_name mentionned as a parameter.

        Args:
            list_dicts (List[Dict[str, str]]): List of dict containing the id and an associated value
            field_name (str): is the string representing the associated value to the id

        Returns:
            Dict[str, str]: dict containing all the information required extracted from the original list of dicts
        """
        new_dict = {}
        for dictio in list_dicts:
            new_dict.update({dictio['id'] : dictio[field_name]})
        return new_dict

    def set_agency_client_token(self, agency_token):
        self.agency_client_token = agency_token

    def round_up_to_base(self, x, base):
        return base * round(x / base)
