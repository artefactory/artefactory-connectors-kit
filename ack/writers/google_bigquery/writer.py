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

from google.cloud import bigquery
from ack import config
from ack.config import logger
from ack.clients.google.client import GoogleClient
from ack.streams.normalized_json_stream import NormalizedJSONStream
from ack.utils.retry import retry
from ack.writers.google_cloud_storage.writer import GoogleCloudStorageWriter
from ack.writers.writer import Writer


class GoogleBigQueryWriter(Writer, GoogleClient):
    _client = None

    def __init__(
        self, dataset, table, bucket, partition_column, write_disposition, location, keep_files,
    ):

        self._project_id = config.PROJECT_ID
        self._client = bigquery.Client(credentials=self._get_credentials(), project=self._project_id)
        self._dataset = dataset
        self._table = table
        self._bucket = bucket
        self._partition_column = partition_column
        self._write_disposition = write_disposition
        self._location = location
        self._keep_files = keep_files

    @retry
    def write(self, stream):

        normalized_stream = NormalizedJSONStream.create_from_stream(stream)

        gcs_writer = GoogleCloudStorageWriter(self._bucket, self._project_id)
        gcs_uri, blob = gcs_writer.write(normalized_stream)

        table_ref = self._get_table_ref()

        load_job = self._client.load_table_from_uri(gcs_uri, table_ref, job_config=self.job_config())

        logger.info(f"Loading data into BigQuery {self._dataset}:{self._table}")
        result = load_job.result()

        assert result.state == "DONE"

        if not self._keep_files:
            logger.info(f"Deleting GCS file: {gcs_uri}")
            blob.delete()

    def _get_dataset(self):
        dataset_ref = self._client.dataset(self._dataset)
        return bigquery.Dataset(dataset_ref)

    def _get_table_ref(self):
        dataset = self._get_dataset()
        return dataset.table(self._table)

    def job_config(self):
        job_config = bigquery.LoadJobConfig()
        job_config.create_disposition = bigquery.job.CreateDisposition.CREATE_IF_NEEDED
        job_config.source_format = bigquery.job.SourceFormat.NEWLINE_DELIMITED_JSON
        job_config.autodetect = True

        if self._write_disposition == "truncate":
            job_config.write_disposition = bigquery.job.WriteDisposition.WRITE_TRUNCATE
        elif self._write_disposition == "append":
            job_config.write_disposition = bigquery.job.WriteDisposition.WRITE_APPEND
        else:
            raise Exception("Unknown BigQuery write disposition")

        if self._partition_column:
            job_config.time_partitioning = bigquery.table.TimePartitioning(
                bigquery.table.TimePartitioningType.DAY, self._partition_column
            )

        return job_config
