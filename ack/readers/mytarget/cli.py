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
from ack.readers.mytarget.config import REQUEST_TYPES
from ack.readers.mytarget.reader import MyTargetReader
from ack.utils.args import extract_args
from ack.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS
from ack.utils.processor import processor


@click.command(name="read_mytarget")
@click.option("--mytarget-client-id", required=True)
@click.option("--mytarget-client-secret", required=True)
@click.option("--mytarget-refresh-token", required=True)
@click.option("--mytarget-request-type", type=click.Choice(REQUEST_TYPES), required=True)
@click.option(
    "--mytarget-date-range",
    type=click.Choice(DEFAULT_DATE_RANGE_FUNCTIONS.keys()),
    help=f"One of the available ACK default date ranges: {DEFAULT_DATE_RANGE_FUNCTIONS.keys()}",
)
@click.option("--mytarget-start-date", type=click.DateTime())
@click.option("--mytarget-end-date", type=click.DateTime())
@processor("mytarget_client_secret", "mytarget_refresh_token")
def mytarget(**kwargs):
    return MyTargetReader(**extract_args("mytarget_", kwargs))
