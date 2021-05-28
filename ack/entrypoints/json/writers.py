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
from ack.writers.amazon_s3.config import AmazonS3WriterConfig
from ack.writers.azure_blob_storage.config import AzureBlobStorageWriterConfig
from ack.writers.azure_blob_storage.writer import AzureBlobStorageWriter
from ack.writers.google_bigquery.config import GoogleBigQueryWriterConfig
from ack.writers.google_cloud_storage.config import GoogleCloudStorageWriterConfig
from ack.writers.local.config import LocalWriterConfig
from ack.writers.amazon_s3.writer import AmazonS3Writer
from ack.writers.console.writer import ConsoleWriter
from ack.writers.google_bigquery.writer import GoogleBigQueryWriter
from ack.writers.google_cloud_storage.writer import GoogleCloudStorageWriter
from ack.writers.local.writer import LocalWriter


writers_classes = {
    "amazon_s3": (AmazonS3Writer, AmazonS3WriterConfig),
    "console": (ConsoleWriter,),
    "google_bigquery": (GoogleBigQueryWriter, GoogleBigQueryWriterConfig),
    "google_cloud_storage": (GoogleCloudStorageWriter, GoogleCloudStorageWriterConfig),
    "local": (LocalWriter, LocalWriterConfig),
    "azure_blob_storage": (AzureBlobStorageWriter, AzureBlobStorageWriterConfig),
}
