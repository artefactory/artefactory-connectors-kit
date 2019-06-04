from functools import update_wrapper


def processor(f):
    """Helper decorator to rewrite a function so that it returns another
    function from it.
    """
    def new_func(*args, **kwargs):
        def processor():
            return f(*args, **kwargs)

        return update_wrapper(processor, f)
    return update_wrapper(new_func, f)


#
#
# # def app_command(func):
# #     @click.option('--gcs-bucket', help="GCS Bucket", required=True)
# #     @click.option('--gcs-prefix', help="GCS Prefix")
# #     @click.option('--bq-dataset', help="BigQuery Dataset", required=True)
# #     @click.option('--bq-table', help="BigQuery Table", required=True)
# #     @click.option('--bq-schema', help="BigQuery Schema")
# #     @click.option('--bq-partition-field', help="BigQuery Partition Field", default=None)
# #     @click.option('--bq-append', help="Overwrite or append BigQuery data", is_flag=True)
# #     def function_wrapper(**kwargs):
# #         reader = func(**kwargs)
# #         execute_runner(reader, **kwargs)
# #     return function_wrapper
#
#
# reader = processor
# writer = processor
