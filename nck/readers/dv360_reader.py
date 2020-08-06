import click
import logging
import io
from nck.readers.reader import Reader
from nck.utils.file_reader import unzip
from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload
from oauth2client import client, GOOGLE_REVOKE_URI
import httplib2
from time import sleep
from tenacity import retry, wait_exponential, stop_after_delay

@click.command(name="read_dv360")
@click.option("--dv360-access-token", default=None)
@click.option("--dv360-refresh-token", required=True)
@click.option("--dv360-client-id", required=True)
@click.optiom("--dv360-client-secret", required=True)



class DV360Reader(Reader):

    API_NAME="displayvideo"
    API_VERSION="v1"

    def __init__(
        self,
        acces_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
        **kwargs
        ):
        credentials = client.GoogleCredentials(
            acces_token,
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

    def validate_inputs(self):
        raise NotImplementedError


    # make sure to implement the appropriate retry policy.
    @retry(
        wait=wait_exponential(multiplier=1, min=60, max=3600),
        stop=stop_after_delay(36000),
    )
    def _wait_sdf_download_request(self, operation):
        logging.info(
            f"waiting for SDF operation: {operation['name']} to complete running"
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

    # create a sdf asynchronous task of type googleapiclient.discovery.Resource
    # and return its metada.
    def create_sdf_task(
        self,
        file_type, 
        filter_type, 
        advertiser_id,
        version="SDF_VERSION_5_2"):

        body = {
            "parentEntityFilter": {
                "fileType": file_type,
                "filterType": filter_type
            },
            "version": version,
            "advertiserId": advertiser_id
        }

        operation = self._client.sdfdownloadtasks().create(body=body).execute()
        logging.info("Operation %s was created." % operation["name"])
        return operation
    
    def download_sdf(self, operation):
        request = self._client.media().download(resourceName=operation["response"]["resourceName"])
        request.uri = request.uri.replace("?alt=json", "?alt=media")
        file_name = "sdf"
        sdf = io.FileIO(f"/tmp/{file_name}.zip", mode="wb")
        downloader = MediaIoBaseDownload(sdf, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logging.info(f"Download {int(status.progress() * 100)}.")

    # TODO: Exctract file type from parameter
    def _get_file_type(self):
        return "FILE_TYPE_INSERTION_ORDER"

    # TODO: Extract filter type from parameter
    def _get_filter_type(self):
        return "FILTER_TYPE_NONE"

    # TODO: Exctract advertiser id from parameter
    def _get_advertiser_id(self):
        return "4768432"

    def read(self):
        # exctract request body from parameters
        file_type = self._get_file_type()
        filter_type = self._get_filter_type()
        advertiser_id = self._get_advertiser_id()
        # create sdf task
        init_operation = self.create_sdf_task(file_type, filter_type, advertiser_id)
        # wait for the task to be ready or raise Error
        created_operation = self._wait_sdf_download_request(init_operation)
        # download the sdf file and unzip it
        file_name = "sdf.zip"
        self.download_sdf(created_operation)
        unzip(f"/tmp/{file_name}", output_path="/tmp")

        

        