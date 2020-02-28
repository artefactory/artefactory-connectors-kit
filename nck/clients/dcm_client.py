import logging
import httplib2

from oauth2client import client, GOOGLE_TOKEN_URI
from googleapiclient import discovery

logger = logging.getLogger("CM_client")


class DCMClient:
    API_NAME = "dfareporting"
    API_VERSION = "v3.3"

    def __init__(self, access_token, client_id, client_secret, refresh_token):
        # self._access_token = access_token,
        # self._client_id = client_id,
        # self._client_secret = client_secret,
        # self._refresh_token = refresh_token,
        self._credentials = client.GoogleCredentials(
            access_token=access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            token_expiry=None,
            token_uri=GOOGLE_TOKEN_URI,
            user_agent=None,
        )
        http = self._credentials.authorize(httplib2.Http())
        self._credentials.refresh(http)
        self.auth = (
            self._credentials.token_response["token_type"] + " " + self._credentials.token_response["access_token"]
        )
        self._service = discovery.build(self.API_NAME, self.API_VERSION, http=http, cache_discovery=False)
