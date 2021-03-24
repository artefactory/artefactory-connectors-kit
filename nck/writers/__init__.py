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
from nck.writers.amazon_s3.config import AmazonS3WriterConfig
from nck.writers.google_bigquery.config import GoogleBigQueryWriterConfig
from nck.writers.google_cloud_storage.config import GoogleCloudStorageWriterConfig
from nck.writers.local.config import LocalWriterConfig
from nck.writers.writer import Writer
from nck.writers.amazon_s3.writer import AmazonS3Writer
from nck.writers.console.writer import ConsoleWriter
from nck.writers.google_bigquery.writer import GoogleBigQueryWriter
from nck.writers.google_cloud_storage.writer import GoogleCloudStorageWriter
from nck.writers.local.writer import LocalWriter

from nck.writers.amazon_s3.cli import amazon_s3
from nck.writers.console.cli import console
from nck.writers.google_bigquery.cli import google_bigquery
from nck.writers.google_cloud_storage.cli import google_cloud_storage
from nck.writers.local.cli import local

writers = [amazon_s3, console, google_bigquery, google_cloud_storage, local]

writer_classes = {
    "amazon-s3": (AmazonS3Writer, AmazonS3WriterConfig),
    "console": (ConsoleWriter,),
    "google-bigquery": (GoogleBigQueryWriter, GoogleBigQueryWriterConfig),
    "google-cloud-storage": (GoogleCloudStorageWriter, GoogleCloudStorageWriterConfig),
    "local": (LocalWriter, LocalWriterConfig),
}

__all__ = ["writers", "Writer", "writer_classes"]
