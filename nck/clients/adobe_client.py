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

import logging
from datetime import datetime, timedelta
import requests
import jwt

from nck.utils.retry import retry

IMS_HOST = "ims-na1.adobelogin.com"
IMS_EXCHANGE = "https://ims-na1.adobelogin.com/ims/exchange/jwt"

logging.basicConfig(level="INFO")
logger = logging.getLogger()


class AdobeClient:
    """
    Create an Adobe Client for JWT Authentification.
    Doc: https://github.com/AdobeDocs/adobeio-auth/blob/stage/JWT/JWT.md
    Most of the code is taken from this repo:
    https://github.com/AdobeDocs/analytics-2.0-apis/tree/master/examples/jwt/python
    """

    @retry
    def __init__(
        self, client_id, client_secret, tech_account_id, org_id, private_key,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tech_account_id = tech_account_id
        self.org_id = org_id
        self.private_key = private_key

        # Creating jwt_token attribute
        logging.info("Getting jwt_token.")
        self.jwt_token = jwt.encode(
            {
                "exp": datetime.utcnow() + timedelta(seconds=30),
                "iss": self.org_id,
                "sub": self.tech_account_id,
                f"https://{IMS_HOST}/s/ent_analytics_bulk_ingest_sdk": True,
                "aud": f"https://{IMS_HOST}/c/{self.client_id}",
            },
            self.private_key,
            algorithm="RS256",
        )

        # Creating access_token attribute
        logging.info("Getting access_token.")
        post_body = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "jwt_token": self.jwt_token,
        }
        response = requests.post(IMS_EXCHANGE, data=post_body)
        self.access_token = response.json()["access_token"]

    def build_request_headers(self, global_company_id):
        """
        Build request headers to be used to interract with Adobe Analytics APIs 2.0.
        """
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "x-api-key": self.client_id,
            "x-proxy-global-company-id": global_company_id,
        }
