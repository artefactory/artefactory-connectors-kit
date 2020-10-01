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

import base64
import requests
from itertools import chain
import click
from click import ClickException

from nck.utils.args import extract_args
from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.helpers.confluence_helper import parse_response, CUSTOM_FIELDS
from nck.streams.json_stream import JSONStream
from nck.streams.normalized_json_stream import NormalizedJSONStream

RECORDS_PER_PAGE = 100
CONTENT_ENDPOINT = "wiki/rest/api/content"


@click.command(name="read_confluence")
@click.option(
    "--confluence-user-login",
    required=True,
    help="User login associated with your Atlassian account"
)
@click.option(
    "--confluence-api-token",
    required=True,
    help="API token associated with your Atlassian account"
)
@click.option(
    "--confluence-atlassian-domain",
    required=True,
    help="Atlassian domain under which the content to request is located"
)
@click.option(
    "--confluence-content-type",
    type=click.Choice(["page", "blogpost"]),
    default="page",
    help="Type of content on which the report should be filtered"
)
@click.option(
    "--confluence-spacekey",
    multiple=True,
    help="Space keys on which the report should be filtered"
)
@click.option(
    "--confluence-field",
    required=True,
    multiple=True,
    help="Fields that should be included in the report (path.to.field.value or custom_field)"
)
@click.option(
    "--confluence-normalize-stream",
    type=click.BOOL,
    default=False,
    help="If set to True, yields a NormalizedJSONStream (spaces and special "
    "characters replaced by '_' in field names, which is useful for BigQuery). "
    "Else, yields a standard JSONStream."
)
@processor("confluence_user_login", "confluence_api_token")
def confluence(**kwargs):
    return ConfluenceReader(**extract_args("confluence_", kwargs))


class ConfluenceReader(Reader):

    def __init__(
        self,
        user_login,
        api_token,
        atlassian_domain,
        content_type,
        spacekey,
        field,
        normalize_stream
    ):
        self.user_login = user_login
        self.api_token = api_token
        self.build_headers()
        self.atlassian_domain = atlassian_domain
        self.content_type = content_type
        self.spacekeys = list(spacekey)
        self.fields = list(field)
        self.normalize_stream = normalize_stream

        self.validate_spacekeys()

    def validate_spacekeys(self):
        requirements = [
            CUSTOM_FIELDS[field]["specific_to_spacekeys"] for field in self.fields
            if field in CUSTOM_FIELDS and "specific_to_spacekeys" in CUSTOM_FIELDS[field]
        ]
        if len(requirements) > 0:
            inter_requirements = (
                requirements[0] if len(requirements) == 1
                else list(set(requirements[0]).intersection(*requirements[1:]))
            )
            if len(inter_requirements) == 0:
                raise ClickException("Invalid request. No intersection found between spacekey requirements.")
            elif self.spacekeys != inter_requirements:
                raise ClickException(f"Invalid request. Spacekeys should be set to '{inter_requirements}'.")

    def build_headers(self):
        api_login = f"{self.user_login}:{self.api_token}"
        encoded_bytes = base64.b64encode(api_login.encode("utf-8"))
        encoded_string = str(encoded_bytes, "utf-8")
        self.headers = {
            "Authorization": f"Basic {encoded_string}",
            "Content-Type": "application/json"
        }

    def build_params(self):
        api_fields = [
            CUSTOM_FIELDS[field]["source_field"]
            if field in CUSTOM_FIELDS
            else field for field in self.fields
        ]
        return {"type": self.content_type, "expand": ",".join(api_fields)}

    def get_raw_response(self, page_nb, spacekey=None):
        params = self.build_params()
        params["start"] = page_nb * RECORDS_PER_PAGE
        params["limit"] = RECORDS_PER_PAGE
        if spacekey is not None:
            params["spaceKey"] = spacekey

        url = f"{self.atlassian_domain}/{CONTENT_ENDPOINT}"
        response = requests.get(url, headers=self.headers, params=params)
        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def get_report_generator(self, spacekey=None):
        page_nb = 0
        raw_response = self.get_raw_response(page_nb, spacekey)
        all_responses = [parse_response(raw_response, self.fields)]

        while raw_response["_links"].get("next"):
            page_nb += 1
            raw_response = self.get_raw_response(page_nb, spacekey)
            all_responses.append(parse_response(raw_response, self.fields))

        return chain(*all_responses)

    def get_aggregated_report_generator(self):
        if self.spacekeys:
            for spacekey in self.spacekeys:
                yield from self.get_report_generator(spacekey)
        else:
            yield from self.get_report_generator()

    def read(self):
        if self.normalize_stream:
            yield NormalizedJSONStream("results_", self.get_aggregated_report_generator())
        else:
            yield JSONStream("results_", self.get_aggregated_report_generator())
