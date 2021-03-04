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
from nck.commands.command import processor
from nck.readers.radarly.reader import RadarlyReader
from nck.utils.args import extract_args


@click.command(name="read_radarly")
@click.option("--radarly-pid", required=True, type=click.INT, help="Radarly Project ID")
@click.option("--radarly-client-id", required=True, type=click.STRING)
@click.option("--radarly-client-secret", required=True, type=click.STRING)
@click.option(
    "--radarly-focus-id",
    required=True,
    multiple=True,
    type=click.INT,
    help="Focus IDs (from Radarly queries)",
)
@click.option(
    "--radarly-start-date",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]),
)
@click.option(
    "--radarly-end-date",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]),
)
@click.option(
    "--radarly-api-request-limit",
    default=250,
    type=click.INT,
    help="Max number of posts per API request",
)
@click.option(
    "--radarly-api-date-period-limit",
    default=int(1e4),
    type=click.INT,
    help="Max number of posts in a single API search query",
)
@click.option(
    "--radarly-api-quarterly-posts-limit",
    default=int(45e3),
    type=click.INT,
    help="Max number of posts requested in the window (usually 15 min) (see Radarly documentation)",
)
@click.option(
    "--radarly-api-window",
    default=300,
    type=click.INT,
    help="Duration of the window (usually 300 seconds)",
)
@click.option(
    "--radarly-throttle",
    default=True,
    type=click.BOOL,
    help="""If set to True, forces the connector to abide by official Radarly API limitations
         (using the api-quarterly-posts-limit parameter)""",
)
@click.option("--radarly-throttling-threshold-coefficient", default=0.95, type=click.FLOAT)
@processor("radarly_client_id", "radarly_client_secret")
def radarly(**kwargs):
    return RadarlyReader(**extract_args("radarly_", kwargs))
