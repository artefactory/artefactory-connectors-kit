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

import time
from http import HTTPStatus
from typing import Dict, Tuple

import nck.clients.api.helper as api_client_helper
from click import ClickException
from nck.clients.api.client import ApiClient
from nck.config import logger
from nck.readers.reader import Reader
from nck.readers.yandex_statistics.config import YANDEX_DIRECT_API_BASE_URL
from nck.streams.json_stream import JSONStream
from nck.utils.text import get_report_generator_from_flat_file


class YandexStatisticsReader(Reader):
    def __init__(
        self,
        token,
        fields: Tuple[str],
        report_type: str,
        report_name: str,
        date_range: str,
        include_vat: bool,
        **kwargs,
    ):
        self.token = token
        self.fields = list(fields)
        self.report_type = report_type
        self.report_name = report_name
        self.date_range = date_range
        self.include_vat = include_vat
        self.kwargs = kwargs

    def result_generator(self):
        api_client = ApiClient(self.token, YANDEX_DIRECT_API_BASE_URL)
        body = self._build_request_body()
        headers = self._build_request_headers()
        while True:
            response = api_client.execute_request(url="reports", body=body, headers=headers, stream=True)
            if response.status_code == HTTPStatus.CREATED:
                waiting_time = int(response.headers["retryIn"])
                logger.info(f"Report added to queue. Should be ready in {waiting_time} min.")
                time.sleep(waiting_time * 60)
            elif response.status_code == HTTPStatus.ACCEPTED:
                logger.info("Report in queue.")
            elif response.status_code == HTTPStatus.OK:
                logger.info("Report successfully retrieved.")

                return get_report_generator_from_flat_file(
                    response.iter_lines(),
                    delimiter="\t",
                    skip_n_first=1,
                )

                return get_report_generator_from_flat_file(
                    response.iter_lines(),
                    delimiter="\t",
                    skip_n_first=1,
                )

            elif response.status_code == HTTPStatus.BAD_REQUEST:
                logger.error("Invalid request.")
                logger.error(response.json())
                break
            elif response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                logger.error("Internal server error.")
                logger.error(response.json())
                break
            else:
                logger.error(response.json())
                break
        return None

    def _build_request_body(self) -> Dict:
        body = {}
        selection_criteria = self._add_custom_dates_if_set()
        if len(self.kwargs["filters"]) > 0:
            selection_criteria["Filter"] = [
                api_client_helper.get_dict_with_keys_converted_to_new_string_format(
                    field=filter_element[0],
                    operator=filter_element[1],
                    values=filter_element[2],
                )
                for filter_element in self.kwargs["filters"]
            ]
        body["params"] = api_client_helper.get_dict_with_keys_converted_to_new_string_format(
            selection_criteria=selection_criteria,
            field_names=self.fields,
            report_name=self.report_name,
            report_type=self.report_type,
            date_range_type=self.date_range,
            format="TSV",
            include_v_a_t="YES" if self.include_vat else "NO",
        )
        if self.kwargs["max_rows"] is not None:
            body["params"]["Page"] = api_client_helper.get_dict_with_keys_converted_to_new_string_format(
                limit=self.kwargs["max_rows"]
            )
        return body

    def _build_request_headers(self) -> Dict:
        return {
            "skipReportSummary": "true",
            "Accept-Language": self.kwargs["report_language"],
        }

    def _add_custom_dates_if_set(self) -> Dict:
        selection_criteria = {}
        if self.kwargs["date_start"] is not None and self.kwargs["date_stop"] is not None and self.date_range == "CUSTOM_DATE":
            selection_criteria["DateFrom"] = self.kwargs["date_start"].strftime("%Y-%m-%d")
            selection_criteria["DateTo"] = self.kwargs["date_stop"].strftime("%Y-%m-%d")
        elif (
            self.kwargs["date_start"] is not None and self.kwargs["date_stop"] is not None and self.date_range != "CUSTOM_DATE"
        ):
            raise ClickException("Wrong date range. If start and stop dates are set, should be CUSTOM_DATE.")
        elif (
            self.kwargs["date_start"] is not None or self.kwargs["date_stop"] is not None
        ) and self.date_range != "CUSTOM_DATE":
            raise ClickException(
                (
                    "Wrong combination of date parameters. "
                    "Only use date start and date stop with date range set to CUSTOM_DATE."
                )
            )
        elif (self.kwargs["date_start"] is None or self.kwargs["date_stop"] is None) and self.date_range == "CUSTOM_DATE":
            raise ClickException("Missing at least one date. Have you set start and stop dates?")
        return selection_criteria

    def read(self):
        yield JSONStream(f"results_{self.report_type}", self.result_generator())
