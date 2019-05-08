import click

from lib.builder import Builder


def app_default_options(func):
    @click.option('--gcs-bucket', help="GCS Bucket without gs:// and without project name", required=True)
    @click.option('--gcs-folder', help="GCS Folder")
    @click.option('--bq-dataset', help="BigQuery Dataset", required=True)
    @click.option('--bq-table', help="BigQuery Table", required=True)
    @click.option('--bq-schema', help="BigQuery Schema")
    @click.option('--bq-partition-field', help="BigQuery Partition Field", default=None)
    @click.option('--bq-append', help="BigQuery Partition Field", is_flag=True)
    def function_wrapper(**kwargs):
        reader = func(**kwargs)
        execute_builder(reader, **kwargs)
    return function_wrapper


def execute_builder(reader, **kwargs):
    gcs_writer_args = {
        "bucket": kwargs.get("gcs_bucket"),
        "folder": kwargs.get("gcs_folder")
    }
    bq_writer_args = {
        "dataset": kwargs.get("bq_dataset"),
        "table": kwargs.get("bq_table"),
        "schema": kwargs.get("bq_schema"),
        "partition_field": kwargs.get("bq_partition_field", None),
        "append":  kwargs.get("bq_append", False),
    }
    builder = Builder(
        reader,
        gcs_writer_args,
        bq_writer_args
    )
    builder.execute()
