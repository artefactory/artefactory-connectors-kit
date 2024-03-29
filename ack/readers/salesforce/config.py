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
from pydantic import BaseModel

SALESFORCE_LOGIN_ENDPOINT = "https://login.salesforce.com/services/oauth2/token"
SALESFORCE_LOGIN_REDIRECT = "https://login.salesforce.com/services/oauth2/success"
SALESFORCE_SERVICE_ENDPOINT = "https://eu16.force.com"
SALESFORCE_QUERY_ENDPOINT = "/services/data/v42.0/query/"
SALESFORCE_DESCRIBE_ENDPOINT = "/services/data/v42.0/sobjects/{obj}/describe"


class SalesforceReaderConfig(BaseModel):
    consumer_key: str
    consumer_secret: str
    user: str
    password: str
    object_type: str = None
    query: str = None
    query_name: str = None
    watermark_column: str
    watermark_init: str
    query: str
    query_name: str
    table: str
    redis_state_service_name: str
    redis_state_service_host: str
    redis_state_service_port: int = 6379
