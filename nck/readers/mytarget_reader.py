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
import itertools
from datetime import date, datetime
from typing import Any, Dict, List, Tuple
import click
import requests
from tenacity import retry, wait_exponential, stop_after_delay
from nck.commands.command import processor
from nck.helpers.mytarget_helper import REQUEST_CONFIG, REQUEST_TYPES
from nck.readers.reader import Reader
from nck.streams.json_stream import JSONStream
from nck.utils.exceptions import MissingItemsInResponse
from nck.utils.args import extract_args
from nck.utils.date_handler import (
    DEFAULT_DATE_RANGE_FUNCTIONS,
    check_date_range_definition_conformity,
    get_date_start_and_date_stop_from_date_range,
)


@click.command(name="read_mytarget")
@click.option("--mytarget-client-id", required=True)
@click.option("--mytarget-client-secret", required=True)
@click.option("--mytarget-refresh-token", required=True)
@click.option("--mytarget-request-type", type=click.Choice(REQUEST_TYPES), required=True)
@click.option(
    "--mytarget-date-range",
    type=click.Choice(DEFAULT_DATE_RANGE_FUNCTIONS.keys()),
    help=f"One of the available NCK default date ranges: {DEFAULT_DATE_RANGE_FUNCTIONS.keys()}",
)
@click.option("--mytarget-start-date", type=click.DateTime())
@click.option("--mytarget-end-date", type=click.DateTime())
@processor("mytarget-client-id", "mytarget-client-secret")
def mytarget(**kwargs):
    return MyTargetReader(**extract_args("mytarget_", kwargs))


LIMIT_REQUEST_MYTARGET = 20


class MyTargetReader(Reader):
    def __init__(self, client_id, client_secret, refresh_token, request_type, date_range, start_date, end_date, **kwargs):
        check_date_range_definition_conformity(start_date, end_date, date_range)
        start_date, end_date = self.__get_valid_start_date_end_date(date_range, start_date, end_date)
        self.client_id = client_id
        self.client_secret = client_secret
        self.agency_client_token = {"refresh_token": refresh_token}
        self.request_type = request_type
        self.date_range = date_range
        self.start_date = start_date
        self.start_date = end_date
        self.date_format = kwargs.get("date_format")
        self.date_are_valid = self.__check_date_input_validity()
        self.__retrieve_and_set_token()

    def read(self):
        if self.date_are_valid:
            if self.request_type == "performance":
                dict_stat, dict_camp, dict_banner = self.__retrieve_all_data()

                complete_daily_content = self.map_campaign_name_to_daily_stat(dict_stat, dict_camp, dict_banner)
                yield JSONStream("mytarget_performance_", self.split_content_by_date(complete_daily_content))
            if self.request_type == "budget":
                res_dates = self.__get_all_results("get_campaign_dates")
                res_budgets = self.__get_all_results("get_campaign_budgets")

                budget_with_dates = self.map_budget_to_date_range(res_dates, res_budgets)
                yield JSONStream("mytarget_budget_", self.__yield_from_list(budget_with_dates))

    def __check_date_input_validity(self) -> bool:
        """The goal of this function is to check the validity of the date input parameters before retrieving the data."""
        return self.__check_end_posterior_to_start(self.start_date, self.end_date) and self.__check_date_not_in_future(
            self.end_date
        )

    def __check_date_not_in_future(self, end_date: datetime) -> bool:
        if end_date <= date.today():
            return True
        else:
            raise ValueError(f"The end date {end_date} is posterior to current date {date.today()}")

    def __check_end_posterior_to_start(self, start_date: datetime, end_date: datetime) -> bool:
        if start_date > end_date:
            raise ValueError(f"The start date {start_date} is posterior to end date {end_date}")
        else:
            return True

    def __get_valid_start_date_end_date(self, date_range: str, start_date: datetime, end_date: datetime):
        if date_range is not None:
            return get_date_start_and_date_stop_from_date_range(date_range)
        else:
            return (start_date.date(), end_date.date())

    def __retrieve_and_set_token(self):
        """In order to request the api, we need an active token. To do so we use the token which
        was provided to get a new one which is going to be active for a day. Once done we set it
        as an attribute.
        """
        parameters_refresh_token = self.__generate_params_dict("refresh_agency_token")
        request_refresh_token = self.__create_request("refresh_agency_token", parameters_refresh_token)
        refreshed_token = requests.post(**request_refresh_token).json()
        self.set_agency_client_token(refreshed_token)

    def __retrieve_all_data(self) -> Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]]:

        response_camp_id_name = self.__get_all_results("get_campaign_ids_names")
        response_banner_id_name = self.__get_all_results("get_banner_ids_names")
        response_daily_stat = self.__get_response("get_banner_stats")

        dict_stat = self.__transform_list_dict_to_dict(response_daily_stat["items"])
        dict_camp = self.__transform_list_dict_to_dict(response_camp_id_name)
        dict_banner = self.__transform_list_dict_to_dict(response_banner_id_name)

        return dict_stat, dict_camp, dict_banner

    def __get_all_results(self, name_content: str, offset=0) -> List[Dict[str, str]]:
        """Based on the __get_response function this function is incrementing through offsets according to the
        number of elements given by the first response.

        Args:
            name_content (str): string representing key of parameters config dict
            offset (int, optional): potential offset of the request. Defaults to 0.

        Returns:
            List[Dict[str, Any]]: list of dicts resulting from the requests we made to the api
        """
        first_elements = self.__get_response(name_content)
        count = first_elements["count"]
        elements = [first_elements["items"]]
        if count > LIMIT_REQUEST_MYTARGET:
            elements += [
                self.__get_response(name_content, offset=offset)["items"]
                for offset in range(
                    LIMIT_REQUEST_MYTARGET, self.round_up_to_base(count, LIMIT_REQUEST_MYTARGET), LIMIT_REQUEST_MYTARGET
                )
            ]
        return list(itertools.chain.from_iterable(elements))

    def map_campaign_name_to_daily_stat(
        self, dict_stat: Dict[str, str], dict_camp: List[Dict[str, str]], dict_banner: Dict[str, str]
    ) -> List[Dict[str, str]]:
        unused_banners = []
        for ban_id in dict_banner.keys():
            if dict_banner[ban_id]["campaign_id"] in dict_camp.keys():
                dict_banner[ban_id]["campaign_name"] = dict_camp[dict_banner[ban_id]["campaign_id"]]["name"]
                dict_banner[ban_id]["rows"] = dict_stat[dict_banner[ban_id]["id"]]["rows"]
            else:
                unused_banners.append(ban_id)
        for unused_ban_id in unused_banners:
            dict_banner.pop(unused_ban_id)
        return dict_banner

    def map_budget_to_date_range(
        self, dates: Dict[str, str], budgets: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        result = []
        dates_dict = self.__transform_list_dict_to_dict(dates)
        for budget in budgets:
            budget["date_start"] = dates_dict[budget["id"]]["date_start"]
            budget["date_end"] = dates_dict[budget["id"]]["date_end"]
            budget["status"] = dates_dict[budget["id"]]["status"]
            result.append(budget)
        return result

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
        for key, value in content.items():
            new_line_base = {
                "campaign_id": value["campaign_id"],
                "campaign_name": value["campaign_name"],
                "banner_id": value["id"],
                "banner_name": value.get("name"),
            }
            for dict_daily_stats in value["rows"]:
                if dict_daily_stats["date"] not in dates:
                    dates.append(dict_daily_stats["date"])
                new_line = {**new_line_base, **dict_daily_stats}
                content_by_date.append(new_line)
        yield from content_by_date

    @retry(wait=wait_exponential(multiplier=1, min=1, max=600), stop=stop_after_delay(600))
    def __get_response(self, name_content: str, offset=0) -> Dict[str, Any]:
        """This function makes a request to the api after building eveything necessary to get the
        desired results for a specific need which is defined by name_content.

        Args:
            name_content (str): string representing key of parameters config dict
            offset (int, optional): potential offset of the request. Defaults to 0.

        Returns:
            Dict[str, Any]: dict resulting from the request we made to the api
        """
        parameters = self.__generate_params_dict(name_content, offset=offset)
        request = self.__create_request(name_content, parameters)
        resp = requests.get(**request).json()
        if "items" not in resp.keys():
            raise MissingItemsInResponse("Can't retrieve any item from this response")
        return resp

    def __create_request(self, name_content: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """This function creates the dict with all the parameters required to query the api

        Args:
            name_content (str): string representing key of parameters config dict
            parameters (Dict[str, Any]): dict of parameters retrieved from get_params_dict

        Returns:
            Dict[str, Any]: dict used to make a request to the api
        """
        req_base = {
            "url": self.__get_url(name_content),
            "headers": self.__get_header(REQUEST_CONFIG[name_content]["headers_type"]),
        }
        return {**req_base, **parameters}

    def __get_url(self, name_content: str) -> str:
        """This function retrieves the url and if it is mandatory to add an id in the url
        we fill if using substitute.

        Args:
            name_content (str): string representing key of parameters config dict

        Returns:
            str: url endpoint
        """
        return REQUEST_CONFIG[name_content]["url"]

    def __get_header(self, header_type: str) -> Dict[str, str]:
        if header_type == "content_type":
            return {"Content-Type": "application/x-www-form-urlencoded", "Host": "target.my.com"}
        elif header_type == "authorization":
            return {"Authorization": "Bearer " + self.agency_client_token["access_token"], "Host": "target.my.com"}

    def __generate_params_dict(self, name_content: str, offset=0) -> Dict[str, Any]:
        """This function returns a dict containing all the parameters required
        for the request.

        Args:
            name_content (str): string representing key of parameters config dict
            offset (int, optional): potential offset of the request. Defaults to 0.

        Returns:
            Dict[str, Any]: params to give to the request dict
        """
        dict_config = REQUEST_CONFIG[name_content]
        params = {}
        if name_content == "refresh_agency_token":
            params["data"] = {
                "grant_type": "refresh_token",
                "refresh_token": self.agency_client_token["refresh_token"],
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        else:
            params["params"] = {}
            if dict_config["offset"]:
                params["params"]["offset"] = offset
            if dict_config["dates_required"]:
                params["params"] = {
                    "date_from": self.start_date.strftime("%Y-%m-%d"),
                    "date_to": self.end_date.strftime("%Y-%m-%d"),
                    "metrics": "all",
                }
        return params

    def set_agency_client_token(self, agency_token: str):
        self.agency_client_token = agency_token

    def round_up_to_base(self, x: int, base: int) -> int:
        return base * round(x / base) + 1

    def __yield_from_list(self, content: List[Dict[str, str]]):
        yield from content

    def __transform_list_dict_to_dict(self, data: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
        return {item["id"]: item for item in data}
