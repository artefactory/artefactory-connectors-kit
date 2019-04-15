# NCK Readers

Each reader role is to read data from external source and transform it into a Stream understable format to be written on GCS and BQ thanks to the corresponding writers.

## Step to create a new Reader

1. Create python script following naming nomenclature ``` [command]_reader.py ```
2. Create object extending [BaseReader](./reader.py) class
3. Choose [Stream type](../streams/README.md) as a class attribute
4. Implement connect, close, list, and read methods
5. Create click command with required options
6. Reference click command into [commands list](./__init__.py)
7. Update current README.md

## Readers list

1. [MySQL](#MySQL-Reader)
2. [Oracle](#Oracle-Reader)
3. [Sheets](#Sheets-Reader)

### MySQL Reader

Query MySQL DB and extract result as JSON Stream

#### Options
```shell
--mysql-host    : SQL server url
--mysql-user    : User name to access db
--mysql-password: User password to access db
--mysql-query   : SQL query to be used to extract data 
```

### Oracle Reader

Query Oracle DB and extract result as JSON Stream

#### Options
```shell
--oracle-host       : Oracle server IP
--oracle-port       : Oracle server port
--oracle-user       : Oracle user to access db
--oracle-password   : Oracle user password
--oracle-database   : Oracle service name
--oracle-query      : SQL query to be used to extract data
```
### Sheets Reader

Extract Google Sheets content as JSON Stream

#### Options
```shell
--sheets-credentials    : Service account information dict
--sheets-file-url       : Google sheets file URL
```


