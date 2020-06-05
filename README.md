# Nautilus Connectors Kit

Nautilus connectors kit is a tool which aim is getting raw data from different sources and store them as-is into different destinations (GCS, BQ, local files, etc.).

## List of connectors

### Readers

- Adobe Analytics 1.4
- Adobe Analytics 2.0
- Amazon S3
- Facebook Marketing
- Google Ads
- Google Analytics
- Google Cloud Storage
- Google Campaign Manager
- Google Display & Video 360
- Google Search Ads 360
- Google Search Console
- Google Sheets
- Oracle
- MySQL
- Radarly
- SalesForce
- Twitter Ads
- Yandex Campaign
- Yandex Statistics

### Writers

- Google BigQuery
- Google Cloud Storage
- Amazon S3
- Local File
- Console (Debug)

## Philosophy

NCK is divided in three main components : Readers, Streams, and Writers.

- [Readers](./nck/readers/README.md) role is to read data from distant sources and transform it into stream object
- [Streams](./nck/streams/README.md) role is to be read as file or line by line. There are local objects usable by writers
- [Writers](./nck/writers/README.md) role is to write stream into distant location

## Usage
**nck** could be consumed through a docker image or can be installed as package and then be used as library or a binary.

### Docker image

1. Build Docker image using `make build_base_image`
2. Run image to get help `docker run --rm nautilus-connector-kit:latest --help`

### Develop with python

First install dependencies with:

```bash
pip install -r requirements.txt
```
Then run:
 
```
python nck/entrypoint.py
```

### Package 

#### Generate distribs :

* Exec cmd `make dist` (it generates a source distrib and a wheel in the created directory dist/)

It is advised to do the following in a virtual env

#### Create a virtual env :

`python3 -m venv testenv; source testenv/bin/activate`

#### Install via the wheel in dist :
`pip wheel --wheel-dir=wheels -r requirements.txt (that creates folder of wheels for packages in requierements)`

`pip install --no-index --find-links=./wheels dist/[nck-file-generated].whl`

#### Install in editable mode :
`pip install -e .`
#### Install via the setup.py :

`python setup.py install`

#### Usage as binary :

* Run cmd `nckrun --help` (which is equivalent to python nck/entrypoint.py)

#### Usage as library : 

`from nck.readers.dbm_reader import DbmReader`

#### Some references on packaging : 


* https://manikos.github.io/a-tour-on-python-packaging
* http://lucumr.pocoo.org/2014/1/27/python-on-wheels/
* https://pip.readthedocs.io/en/1.4.1/cookbook.html#controlling-setup-requires
