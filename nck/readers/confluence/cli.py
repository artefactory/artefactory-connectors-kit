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

import click
from nck.readers.confluence.reader import ConfluenceReader
from nck.utils.args import extract_args
from nck.utils.processor import processor


@click.command(name="read_confluence")
@click.option("--confluence-user-login", required=True, help="User login associated with your Atlassian account")
@click.option("--confluence-api-token", required=True, help="API token associated with your Atlassian account")
@click.option(
    "--confluence-atlassian-domain",
    required=True,
    help="Atlassian domain under which the content to request is located",
)
@click.option(
    "--confluence-content-type",
    type=click.Choice(["page", "blogpost"]),
    default="page",
    help="Type of content on which the report should be filtered",
)
@click.option("--confluence-spacekey", multiple=True, help="Space keys on which the report should be filtered")
@click.option(
    "--confluence-field",
    required=True,
    multiple=True,
    help="Fields that should be included in the report (path.to.field.value or custom_field)",
)
@processor("confluence_user_login", "confluence_api_token")
def confluence(**kwargs):
    return ConfluenceReader(**extract_args("confluence_", kwargs))
