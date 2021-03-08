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
from nck.readers.google_search_console.reader import GoogleSearchConsoleReader
from nck.utils.args import extract_args
from nck.utils.date_handler import DEFAULT_DATE_RANGE_FUNCTIONS
from nck.utils.processor import processor


@click.command(name="read_search_console")
@click.option("--search-console-client-id", required=True)
@click.option("--search-console-client-secret", required=True)
@click.option("--search-console-access-token", default="")
@click.option("--search-console-refresh-token", required=True)
@click.option("--search-console-dimensions", required=True, multiple=True)
@click.option("--search-console-site-url", required=True)
@click.option("--search-console-start-date", type=click.DateTime(), default=None)
@click.option("--search-console-end-date", type=click.DateTime(), default=None)
@click.option("--search-console-date-column", type=click.BOOL, default=False)
@click.option("--search-console-row-limit", type=click.INT, default=25000)
@click.option(
    "--search-console-date-range",
    type=click.Choice(DEFAULT_DATE_RANGE_FUNCTIONS.keys()),
    help=f"One of the available NCK default date ranges: {DEFAULT_DATE_RANGE_FUNCTIONS.keys()}",
)
@processor()
def google_search_console(**params):
    return GoogleSearchConsoleReader(**extract_args("search_console_", params))
