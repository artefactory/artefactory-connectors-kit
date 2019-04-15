# NCK Writers

Writers role is to write Stream object to a local location.

Each writer must implement ```write()``` method.

## Step to create a new Writer

1. Create python script following naming nomenclature ``` [command]_writer.py ```
2. Create object extending [BaseWriter](./writer.py) class
3. Implement write method
6. Update writing strategy in the [Builder.py file](../builder.py).
7. Update current README.md

## Writers list

1. [Google Cloud Storage](#GCS-Writer)
2. [Google Bigquery](#BQ-Writer)

## GCS Writer

Create file from a stream on a local bucket. When written, stream is updated with the GCS url.

## BQ Writer

Create table in the corresponding dataset from stream which has been stored on a GCS Bucket. 

Note: Stream must have gcs_url attribute set.