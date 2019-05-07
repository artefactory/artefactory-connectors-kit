from config import config, logging

from google.cloud import bigquery

from lib.writers.writer import BaseWriter


class BigQueryWriter(BaseWriter):

    _client = None
    _location = "EU"

    def __init__(self, dataset, table, schema=None, partition_field=None):
        self._client = bigquery.Client.from_service_account_json(config.get("GOOGLE_APPLICATION_CREDENTIALS"))

        self._schema = schema
        self._dataset = BigQueryDataset(self._client, dataset)
        self._table = BigQueryTable(self._client, self._dataset, table, self._schema)

        if dataset not in BigQueryDataset.list(self._client):
            self._dataset.create()

        if table not in BigQueryTable.list(self._client, self._dataset):
            self._table.create(partition_field)

    def write(self, stream):
        load_job = self._client.load_table_from_uri(
            stream.get_gcs_url(),
            self._table.ref(),
            job_config=self.job_config()
        )
        job_id = load_job.job_id
        logging.info("Beginning BigQuery job {}".format(job_id))
        load_job.result()
        logging.info("Finishing BigQuery job {}".format(job_id))

    def job_config(self):
        job_config = bigquery.LoadJobConfig()
        if self._schema:
            logging.info("Loading schema from options")
            job_config.schema = self._table.schema
        else:
            logging.info("Detecting schema automatically")
            job_config.autodetect = True
        job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        return job_config


class BigQueryDataset():

    _location = "EU"

    def __init__(self, bq_client, name):
        self._name = name
        self._bq_client = bq_client

    def ref(self):
        return self._bq_client.dataset(self._name)

    def create(self):
        logging.info("Creating dataset {}".format(self._name))
        dataset = bigquery.Dataset(self.ref())
        dataset.location = self._location
        self._bq_client.create_dataset(dataset)

    @staticmethod
    def list(bq_client):
        return [dataset.dataset_id for dataset in bq_client.list_datasets()]


class BigQueryTable():

    _partition_type = "DAY"
    _schema = None

    def __init__(self, bq_client, dataset, name, schema=None):
        self._bq_client = bq_client
        self._dataset = dataset
        self._name = name
        if schema:
            self._schema = self.unroll_schema(schema)

    def ref(self):
        dataset = self._dataset.ref()
        return dataset.table(self._name)

    def create(self, partition_field=None):
        logging.info("Creating table {}".format(self._name))
        table = bigquery.Table(self.ref(), schema=self._schema)
        if partition_field:
            logging.info("Partitioning table with {} column".format(partition_field))
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition_field
            )
        self._bq_client.create_table(table)

    def get(self):
        dataset = self._dataset.ref()
        table = dataset.table(self._name)
        return table.get_table()

    def unroll_schema(self, schema):
        bq_schema_format = []
        for column in schema:
            bq_schema_format.append(
                bigquery.SchemaField(column[0], column[1])
            )
        return bq_schema_format

    @property
    def schema(self):
        return self._schema

    @staticmethod
    def list(bq_client, dataset):
        return [table.table_id for table in bq_client.list_tables(dataset.ref())]
