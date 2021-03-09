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
from nck.utils.args import extract_args
from nck.utils.processor import processor
from nck.writers.google_bigquery.writer import GoogleBigQueryWriter


@click.command(name="write_bq")
@click.option("--bq-dataset", required=True)
@click.option("--bq-table", required=True)
@click.option("--bq-bucket", required=True)
@click.option("--bq-partition-column")
@click.option(
    "--bq-write-disposition",
    default="truncate",
    type=click.Choice(["truncate", "append"]),
)
@click.option("--bq-location", default="EU", type=click.Choice(["EU", "US"]))
@click.option("--bq-keep-files", is_flag=True, default=False)
@processor()
def google_bigquery(**kwargs):
    return GoogleBigQueryWriter(**extract_args("bq_", kwargs))
