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
from ack.readers.google_dv360.config import FILE_TYPES, FILTER_TYPES, REQUEST_TYPES
from ack.readers.google_dv360.reader import GoogleDV360Reader
from ack.utils.args import extract_args
from ack.utils.processor import processor


@click.command(name="read_dv360")
@click.option("--dv360-access-token", default=None, required=True)
@click.option("--dv360-refresh-token", required=True)
@click.option("--dv360-client-id", required=True)
@click.option("--dv360-client-secret", required=True)
@click.option("--dv360-advertiser-id", required=True)
@click.option("--dv360-request-type", type=click.Choice(REQUEST_TYPES), required=True)
@click.option("--dv360-file-type", type=click.Choice(FILE_TYPES), multiple=True)
@click.option("--dv360-filter-type", type=click.Choice(FILTER_TYPES))
@processor("dv360_access_token", "dv360_refresh_token", "dv360_client_secret")
def google_dv360(**kwargs):
    return GoogleDV360Reader(**extract_args("dv360_", kwargs))
