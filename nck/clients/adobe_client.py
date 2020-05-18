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
import datetime
import requests
import jwt

IMS_HOST = "ims-na1.adobelogin.com"
IMS_EXCHANGE = "https://ims-na1.adobelogin.com/ims/exchange/jwt"
DISCOVERY_URL = "https://analytics.adobe.io/discovery/me"

logging.basicConfig(level="INFO")
logger = logging.getLogger()


class JWTClient:
    """
    Following the steps described in this repo:
    https://github.com/AdobeDocs/analytics-2.0-apis/tree/master/examples/jwt/python
    """

    def __init__(
        self,
        api_key,
        tech_account_id,
        org_id,
        client_secret,
        metascopes,
        private_key_path,
    ):
        self.api_key = api_key
        self.tech_account_id = tech_account_id
        self.org_id = org_id
        self.client_secret = client_secret
        self.metascopes = metascopes
        self.private_key_path = private_key_path

        # Creating jwt_token attribute
        logging.info("Getting jwt_token.")
        with open(self.private_key_path, "r") as file:
            private_key = file.read()
        self.jwt_token = jwt.encode(
            {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
                "iss": self.org_id,
                "sub": self.tech_account_id,
                f"https://{IMS_HOST}/s/{self.metascopes}": True,
                "aud": f"https://{IMS_HOST}/c/{self.api_key}",
            },
            private_key,
            algorithm="RS256",
        )

        # Creating access_token attribute
        logging.info("Getting access_token.")
        post_body = {
            "client_id": self.api_key,
            "client_secret": self.client_secret,
            "jwt_token": self.jwt_token,
        }
        response = requests.post(IMS_EXCHANGE, data=post_body)
        self.access_token = response.json()["access_token"]

        # Creating global_company_id attribute
        logging.info("Getting global_company_id.")
        response = requests.get(
            DISCOVERY_URL,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "x-api-key": self.api_key,
            },
        )
        self.global_company_id = (
            response.json().get("imsOrgs")[0].get("companies")[0].get("globalCompanyId")
        )
