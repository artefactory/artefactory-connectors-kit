# NCK Readers

Each reader role is to read data from external source and transform it into a Stream understable format to be written on GCS and BQ thanks to the corresponding writers.

## Step to create a new Reader

1. Create python module following naming nomenclature ``` [command]_reader.py ```
2. Implement `read` method
3. Create click command with required options
4. Reference click command into [commands list](./__init__.py)
5. Update current README.md
