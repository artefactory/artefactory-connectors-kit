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
from ack.readers.awin_advertiser.config import REPORT_TYPES
from ack.readers.awin_advertiser.reader import AwinAdvertiserReader
from ack.utils.args import extract_args
from ack.utils.processor import processor

@click.command(name="read_awin")
@click.option("--awin-auth-token", required=True)
@click.option("--awin-advertiser-id", required=True)
@click.option("--awin-report-type", type = click.Choice(REPORT_TYPES), default = REPORT_TYPES[0])
@click.option("--awin-region", required=True)
@click.option("--awin-timezone", required=True)
@click.option("--awin-start-date", type=click.DateTime())
@click.option("--awin-end-date", default=None, type=click.DateTime())
def awin_advertiser(**kwargs):
    return AwinAdvertiserReader(**extract_args("awin_", kwargs))
