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

import urllib

import requests
from ack.config import logger
from ack.readers.salesforce.config import (
    SALESFORCE_DESCRIBE_ENDPOINT,
    SALESFORCE_LOGIN_ENDPOINT,
    SALESFORCE_LOGIN_REDIRECT,
    SALESFORCE_QUERY_ENDPOINT,
)


class SalesforceClient:
    def __init__(self, user, password, consumer_key, consumer_secret):
        self._user = user
        self._password = password
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret

        self._headers = None
        self._access_token = None
        self._instance_url = None

    @property
    def headers(self):
        return {
            "Content-type": "application/json",
            "Accept-Encoding": "gzip",
            "Authorization": f"Bearer {self.access_token}",
        }

    @property
    def access_token(self):
        if not self._access_token:
            self._load_access_info()

        return self._access_token

    @property
    def instance_url(self):
        if not self._instance_url:
            self._load_access_info()

        return self._instance_url

    def _load_access_info(self):
        logger.info("Retrieving Salesforce access token")

        res = requests.post(SALESFORCE_LOGIN_ENDPOINT, params=self._get_login_params())

        res.raise_for_status()

        self._access_token = res.json().get("access_token")
        self._instance_url = res.json().get("instance_url")

        return self._access_token, self._instance_url

    def _get_login_params(self):
        return {
            "grant_type": "password",
            "client_id": self._consumer_key,
            "client_secret": self._consumer_secret,
            "username": self._user,
            "password": self._password,
            "redirect_uri": SALESFORCE_LOGIN_REDIRECT,
        }

    def _request_data(self, path, params=None):

        endpoint = urllib.parse.urljoin(self.instance_url, path)
        response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)

        response.raise_for_status()

        return response.json()

    def describe(self, object_type):
        path = SALESFORCE_DESCRIBE_ENDPOINT.format(obj=object_type)
        return self._request_data(path)

    def query(self, query):

        logger.info(f"Running Salesforce query: {query}")

        response = self._request_data(SALESFORCE_QUERY_ENDPOINT, {"q": query})

        generating = True

        while generating:

            for rec in response["records"]:
                yield rec

            if "nextRecordsUrl" in response:
                logger.info("Fetching next page of Salesforce results")
                response = self._request_data(response["nextRecordsUrl"])
            else:
                generating = False
