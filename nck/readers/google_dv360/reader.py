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

import io
from itertools import chain
from typing import List

import httplib2
from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload
from nck.config import logger
from nck.readers.google_dv360.config import FILE_NAMES
from nck.readers.reader import Reader
from nck.streams.format_date_stream import FormatDateStream
from nck.streams.json_stream import JSONStream
from nck.utils.exceptions import RetryTimeoutError, SdfOperationError
from nck.utils.file_reader import sdf_to_njson_generator, unzip
from nck.utils.stdout_to_log import http_log, http_log_for_init
from oauth2client import GOOGLE_REVOKE_URI, client
from tenacity import retry, stop_after_delay, wait_exponential


class GoogleDV360Reader(Reader):

    API_NAME = "displayvideo"
    API_VERSION = "v1"
    SDF_VERSION = "SDF_VERSION_5_2"

    # path where to download the sdf file.
    BASE = "/tmp"

    # name of the downloaded archive which may embeds several csv
    # if more than one file type where to be provided.
    ARCHIVE_NAME = "sdf"

    @http_log_for_init("dv360_reader")
    def __init__(self, access_token: str, refresh_token: str, client_id: str, client_secret: str, **kwargs):

        credentials = client.GoogleCredentials(
            access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            token_expiry=None,
            token_uri="https://www.googleapis.com/oauth2/v4/token",
            user_agent=None,
            revoke_uri=GOOGLE_REVOKE_URI,
        )
        http = credentials.authorize(httplib2.Http())
        credentials.refresh(http)

        self._client = discovery.build(self.API_NAME, self.API_VERSION, http=http, cache_discovery=False)

        self.kwargs = kwargs
        self.file_names = self.__get_file_names()

    def __get_file_names(self) -> List[str]:
        """
        DV360 api creates one file per file_type.
        map file_type with the name of the generated file.
        """
        return [f"SDF-{FILE_NAMES[file_type]}" for file_type in self.kwargs.get("file_type")]

    @retry(
        wait=wait_exponential(multiplier=1, min=60, max=3600),
        stop=stop_after_delay(36000),
    )
    def __wait_sdf_download_request(self, operation):
        """
        Wait for a sdf task to be completed. ie. (file ready for download)
            Args:
                operation (dict): task metadata
            Returns:
                operation (dict): task metadata updated with resource location.
        """
        logger.info(f"waiting for SDF operation: {operation['name']} to complete running.")
        get_request = self._client.sdfdownloadtasks().operations().get(name=operation["name"])
        operation = get_request.execute()
        if "done" not in operation:
            raise RetryTimeoutError("The operation has taken more than 10 hours to complete.\n")
        return operation

    def __create_sdf_task(self, body):
        """
        Create a sdf asynchronous task of type googleapiclient.discovery.Resource
            Args:
                body (dict) : request body to describe the data within the generated sdf file.
            Return:
                operation (dict) : contains the task metadata.
        """

        operation = self._client.sdfdownloadtasks().create(body=body).execute()
        logger.info(f"Operation {operation['name']} was created.")
        return operation

    def __download_sdf(self, operation):
        request = self._client.media().download(resourceName=operation["response"]["resourceName"])
        request.uri = request.uri.replace("?alt=json", "?alt=media")
        sdf = io.FileIO(f"{self.BASE}/{self.ARCHIVE_NAME}.zip", mode="wb")
        downloader = MediaIoBaseDownload(sdf, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.info(f"Download {int(status.progress() * 100)}%.")

    def __get_sdf_body(self):
        return {
            "parentEntityFilter": {"fileType": self.kwargs.get("file_type"), "filterType": self.kwargs.get("filter_type")},
            "version": self.SDF_VERSION,
            "advertiserId": self.kwargs.get("advertiser_id"),
        }

    def __get_sdf_objects(self):
        body = self.__get_sdf_body()
        init_operation = self.__create_sdf_task(body=body)
        created_operation = self.__wait_sdf_download_request(init_operation)
        if "error" in created_operation:
            raise SdfOperationError(
                "The operation finished in error with code "
                f"{created_operation['error']['code']}: {created_operation['error']['message']}"
            )
        self.__download_sdf(created_operation)
        unzip(f"{self.BASE}/{self.ARCHIVE_NAME}.zip", output_path=self.BASE)

        # We chain operation if many file_types were to be provided.
        return chain(*[sdf_to_njson_generator(f"{self.BASE}/{file_name}.csv") for file_name in self.file_names])

    def __get_creatives(self):
        response = self._client.advertisers().creatives().list(advertiserId=self.kwargs.get("advertiser_id")).execute()
        if len(response.keys()) == 0:  # no data returned
            return {}
        else:
            all_creatives = response["creatives"]
            while "nextPageToken" in response:
                token = response["nextPageToken"]
                logger.info(f"Query a new page of creatives. Page id: {token}")
                response = (
                    self._client.advertisers()
                    .creatives()
                    .list(advertiserId=self.kwargs.get("advertiser_id"), pageToken=token)
                    .execute()
                )
                all_creatives.extend(response["creatives"])
        yield from all_creatives

    @http_log("dv360_reader")
    def read(self):
        request_type = self.kwargs.get("request_type")
        if request_type == "sdf_request":
            yield FormatDateStream(
                "sdf",
                self.__get_sdf_objects(),
                keys=["Date"],
                date_format=self.kwargs.get("date_format"),
            )
        elif request_type == "creative_request":
            yield JSONStream("advertiser_creatives", self.__get_creatives())
