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

from ack.writers.writer import Writer

from ack.writers.amazon_s3.cli import amazon_s3
from ack.writers.console.cli import console
from ack.writers.google_bigquery.cli import google_bigquery
from ack.writers.google_cloud_storage.cli import google_cloud_storage
from ack.writers.local.cli import local
from ack.writers.azure_blob_storage.cli import azure_blob_storage

writers = [amazon_s3, console, google_bigquery, google_cloud_storage, local, azure_blob_storage]

__all__ = ["writers", "Writer"]
