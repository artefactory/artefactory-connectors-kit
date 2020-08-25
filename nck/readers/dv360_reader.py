
import click
import logging
import io
import httplib2

from itertools import chain
from typing import List, Tuple

from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload
from oauth2client import client, GOOGLE_REVOKE_URI
from tenacity import retry, wait_exponential, stop_after_delay

from nck.helpers.dv360_helper import FILE_NAMES, FILE_TYPES, FILTER_TYPES
from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.utils.file_reader import CSVReader, unzip
from nck.utils.args import extract_args
from nck.streams.format_date_stream import FormatDateStream


@click.command(name="read_dv360")
@click.option("--dv360-access-token", default=None, required=True)
@click.option("--dv360-refresh-token", required=True)
@click.option("--dv360-client-id", required=True)
@click.option("--dv360-client-secret", required=True)
@click.option("--dv360-advertiser-id", required=True)
@click.option("--dv360-file-type", type=click.Choice(FILE_TYPES), multiple=True, required=True)
@click.option("--dv360-filter-type", type=click.Choice(FILTER_TYPES), required=True)
@processor("dbm_access_token", "dbm_refresh_token", "dbm_client_secret")
def dv360(**kwargs):
    return DV360Reader(**extract_args("dv360_", kwargs))


class DV360Reader(Reader):

    API_NAME = "displayvideo"
    API_VERSION = "v1"
    SDF_VERSION = "SDF_VERSION_5_2"

    # path where to download the sdf file.
    BASE = "/tmp"

    # name of the downloaded archive which may embeds several csv
    # if more than one file type where to be provided.
    ARCHIVE_NAME = "sdf"

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
        **kwargs
    ):

        credentials = client.GoogleCredentials(
            access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            token_expiry=None,
            token_uri="https://www.googleapis.com/oauth2/v4/token",
            user_agent=None,
            revoke_uri=GOOGLE_REVOKE_URI
        )
        http = credentials.authorize(httplib2.Http())
        credentials.refresh(http)

        self._client = discovery.build(
            self.API_NAME , self.API_VERSION, http=http, cache_discovery=False
        )

        self.kwargs = kwargs
        self.file_names = self.get_file_names()

    def _get_file_type(self) -> Tuple[str]:
        """
        file_type : dictates the resource type that populates the sdf file.
                    https://developers.google.com/display-video/api/reference/rest/v1/sdfdownloadtasks/create#filetype
                    Required: One can provide several file types.
        """
        return self.kwargs.get("file_type")

    def _get_filter_type(self) -> str:
        """
        filter_type : specifies the type of resource to filter.
                      Required: Only one filter_type allowed.
        """
        return self.kwargs.get("filter_type")

    def _get_advertiser_id(self) -> str:
        return self.kwargs.get("advertiser_id")

    def get_file_names(self) -> List[str]:
        """
        DV360 api creates one file per file_type.
        map file_type with the name of the generated file.
        """
        return [f"SDF-{FILE_NAMES[file_type]}" for file_type in self._get_file_type()]

    @retry(
        wait=wait_exponential(multiplier=1, min=60, max=3600),
        stop=stop_after_delay(36000),
    )
    def _wait_sdf_download_request(self, operation):
        """
        Wait for a sdf task to be completed. ie. (file ready for download)
            Args:
                operation (dict): task metadata
            Returns:
                operation (dict): task metadata updated with resource location.
        """
        logging.info(
            f"waiting for SDF operation: {operation['name']} to complete running."
        )
        get_request = self._client.sdfdownloadtasks().operations().get(name=operation["name"])
        operation = get_request.execute()
        if "done" not in operation:
            raise Exception("The operation has exceed the time limit treshold.\n")
        if "error" in operation:
            raise Exception("The operation finished in error with code %s: %s" % (
                  operation["error"]["code"],
                  operation["error"]["message"]))
        return operation

    def create_sdf_task(self, body):
        """
        Create a sdf asynchronous task of type googleapiclient.discovery.Resource
            Args:
                body (dict) : request body to describe the data within the generated sdf file.
            Return:
                operation (dict) : contains the task metadata.
        """

        operation = self._client.sdfdownloadtasks().create(body=body).execute()
        logging.info("Operation %s was created." % operation["name"])
        return operation

    def download_sdf(self, operation):
        request = self._client.media().download(resourceName=operation["response"]["resourceName"])
        request.uri = request.uri.replace("?alt=json", "?alt=media")
        sdf = io.FileIO(f"{self.BASE}/{self.ARCHIVE_NAME}.zip", mode="wb")
        downloader = MediaIoBaseDownload(sdf, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logging.info(f"Download {int(status.progress() * 100)}.")

    @staticmethod
    def sdf_to_njson_generator(path_to_file):
        csv_reader = CSVReader(csv_delimiter=",", csv_fieldnames=None)
        with open(path_to_file, "rb") as fd:
            dict_reader = csv_reader.read_csv(fd)
            for line in dict_reader:
                yield line

    def get_sdf_body(self):
        # exctract request body from parameters
        file_type = self._get_file_type()
        filter_type = self._get_filter_type()
        advertiser_id = self._get_advertiser_id()
        body = {
            "parentEntityFilter": {
                "fileType": file_type,
                "filterType": filter_type
            },
            "version": self.SDF_VERSION,
            "advertiserId": advertiser_id
        }
        return body

    def get_sdf_objects(self):
        body = self.get_sdf_body()
        init_operation = self.create_sdf_task(body=body)
        created_operation = self._wait_sdf_download_request(init_operation)
        self.download_sdf(created_operation)
        unzip(f"{self.BASE}/{self.ARCHIVE_NAME}.zip", output_path=self.BASE)

        # We chain operation if many file_types were to be provided.
        return chain(
            *[
                self.sdf_to_njson_generator(f"{self.BASE}/{file_name}.csv")
                for file_name in self.file_names
            ]
        )

    def read(self):
        yield FormatDateStream(
            "sdf",
            self.get_sdf_objects(),
            keys=["Date"],
            date_format=self.kwargs.get("date_format"),
        )
