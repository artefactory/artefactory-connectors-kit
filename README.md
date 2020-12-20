# Nautilus Connectors Kit

**NCK is a Command-Line Interface (CLI), allowing you to easily request, stream and store raw reports, from the API source to the destination of your choice.** As of now, the most common output format of data extracted by the application is .njson (i.e. a file of n lines, where each line is a json-like dictionary).

- [Philosophy](#philosophy)
- [Available connectors](#available-connectors)
- [Set-up your developing environment](#set-up-your-developing-environment)
    - [Virtual environment](#virtual-environment)
    - [Linting](#linting)
    - [Pre-commit hooks](#pre-commit-hooks)
    - [TDD (Test-Driven Development)](#tdd-(test-driven-development))
- [Quickstart: launch your first NCK command](#quickstart:-launch-your-first-nck-command)
- [Contribute: we need you!](#contribute:-we-need-you)
    - [How to develop a new reader](#how-to-develop-a-new-reader)
    - [How to develop a new stream](#how-to-develop-a-new-stream)
    - [How to develop a new writer](#how-to-develop-a-new-writer)
- [To go further](#to-go-further)
    - [Build a Docker image of the application and push it to GCP Container Registry](#build-a-docker-image-of-the-application-and-push-it-to-gcp-container-registry)
    - [Package the application to use it as a binary or library](#package-the-application-to-use-it-as-a-binary-or-library)

## Philosophy

The application is composed of **3 main components** (*implemented as Python classes*). When combined, these components act as data connectors, allowing you to stream data from a source to the destination of your choice:

- [Readers](https://github.com/artefactory/nautilus-connectors-kit/tree/dev/nck/readers) are reading data from an API source, and transform it into a stream object.
- [Streams](https://github.com/artefactory/nautilus-connectors-kit/tree/dev/nck/streams) (*transparent to the end-user*) are local objects used by writers to process individual records collected from the source.
- [Writers](https://github.com/artefactory/nautilus-connectors-kit/tree/dev/nck/writers) are writing the output stream object to the destination of your choice.

## Available connectors

As of now, the application is offering:
 
**21 Readers, in various areas such as Media Activation, Website Analytics & many more**
- Adobe Analytics 1.4
- Adobe Analytics 2.0
- Amazon S3
- Confluence
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
- The Trade Desk
- Twitter Ads
- Yandex Campaign
- Yandex Statistics

**5 Writers, including destinations to GCP & AWS cloud platforms**
- Amazon S3   
- Google BigQuery
- Google Cloud Storage
- Local file
- Console (used for debugging)

*A data connector could be, for instance, the combination of a Google Analytics reader + a Google Cloud Storage writer, collecting data from the Google Analytics API, and storing output stream records into a Google Cloud Storage bucket.*

## Set-up your developing environment

To start using NCK and/or contributing, first clone the `dev` branch of this repository:
```
git clone git@github.com:artefactory/nautilus-connectors-kit.git -b dev
```
#### Virtual environment

Create a virtual environment at the root of your local repository:
```
python3 -m venv nck-env
source nck-env/bin/activate
```
Install dependencies:
```
pip install -r requirements.txt
pip install -r requirements-dev.text
```
#### Linting

We are using [black](https://pypi.org/project/black/) and [Flake8](https://flake8.pycqa.org/en/latest/) for code linting.

The black and Flake8 packages have already been installed in your virtual environment with dependencies. Also, a Flake8 configuration file (`.flake8`) and a black configuration file (`pyproject.toml`) are available at the root at this repository.

#### Pre-commit hooks

We are using [pre-commit](https://pre-commit.com/) hooks to point out linting issues in our code before submission to code review.

The pre-commit package has already been installed in your virtual environment with dependencies. Also, a pre-commit configuration file (`.pre-commit-config.yaml`) is available at the root of this repository.

To finalize the installation and install git hooks scripts, execute: `pre-commit install`
For now on, the `pre-commit` command will run automatically on every `git commit`.

#### TDD (*Test-Driven Development*)

We are running tests using [nose](https://nose.readthedocs.io/en/latest/usage.html), an extension of the Python [unittest](https://docs.python.org/fr/3/library/unittest.html) framework.

The nose package has already been installed in your virtual environment with dependencies.
To run existing tests, execute: `nosetests`

## Quickstart: launch your first NCK command

Once this preliminary set-up is finalized, you can start using the application.

NCK commands can be broken down into 3 parts:

**1 - An entrypoint**: all NCK commands are launched through the `nck/entrypoint.py` executable.
```
python nck/entrypoint.py
```
**2 - A reader command, and its options**: in the below example, we are reading Google Analytics data for the view `<VIEW_ID>`, retrieving sessions, pageviews and bounces by date from 2020-01-01 to 2020-01-03.
```
read_ga --ga-client-id <CLIENT_ID> --ga-client-secret <CLIENT_SECRET> --ga-view-id <VIEW_ID> --ga-refresh-token <REFRESH_TOKEN> --ga-dimension ga:date --ga-metric sessions --ga-metric ga:pageviews --ga-metric ga:bounces --ga-start-date 2020-01-01 --ga-end-date 2020-01-03
```
**3 - A writer command, and its options**: in the below example, we are writing the output .nsjon stream into a Google Cloud Storage blob  named `google_analytics_report_2020-01-01.njson`, located under the Google Cloud Storage bucket `nck_extracts`, with the path `FR/google_analytics/`.
```
write_gcs --gcs-project-id <GCP_PROJECT_ID> --gcs-bucket nck_extracts --gcs-prefix FR/google_analytics --gcs-filename google_analytics_report_2020-01-01.njson
```
To execute the NCK command as a whole, we just have to put these 3 parts together.

To simplify your first test, instead of the writer command `write_gcs`, we recommend you to use `write_console`  (*it will write output stream records into your terminal*) or `write_local --local-directory <LOCAL_DESTINATION_DIRECTORY>` (*it will write output stream records into a local file*). In practice, these writer commands are very convenient for debugging, as they are quite simple.

In the end, if we use `write_console` as a writer command, the combined NCK command will be:
```
python nck/entrypoint.py read_ga --ga-client-id <CLIENT_ID> --ga-client-secret <CLIENT_SECRET> --ga-view-id <VIEW_ID> --ga-refresh-token <REFRESH_TOKEN> --ga-dimension ga:date --ga-metric sessions --ga-metric ga:pageviews --ga-metric ga:bounces --ga-start-date 2020-01-01 --ga-end-date 2020-01-03 write_console
```
You can now execute it into your terminal.

**Now that you understand how NCK commands are structured, you can follow these links to find the full documentation on available [reader commands](https://github.com/artefactory/nautilus-connectors-kit/tree/dev/nck/readers) and [writer commands](https://github.com/artefactory/nautilus-connectors-kit/tree/dev/nck/writers).**

## Contribute: we need you!

NCK is an open-source application initially developed by Artefact team: feel free to contribute!
You can find open issues on [this page](https://github.com/artefactory/nautilus-connectors-kit/issues).  If you identify additional enhancements/fixes that could be beneficial to the application, don't hesitate to add them to the list.

Here are a few tips/guidelines to help you efficiently contribute:

### How to develop a new reader

*Readers are reading data from an API source, and transform it into a stream object.*

To create a new reader, you should:

**1 - Create the following modules:
`nck/readers/<SOURCE_NAME>_reader.py`
`nck/helpers/<SOURCE_NAME>_helper.py`**

The `nck/readers/<SOURCE_NAME>_reader.py` module should implement 2 components:

***A click-decorated reader function***
 - The reader function should be **decorated with**: a `@click.command()` decorator, several `@click.option()` decorators (*one for each input that should be provided by end-users*) and a `@processor()` decorator (*preventing secrets to appear in logs*). For further information on how  to implement these decorators, please refer to [click documentation](https://click.palletsprojects.com/en/7.x/).
 - The reader function should return **a reader class** (*more details below*). A source name prefix should be added to the name of each class attribute, using the `extract_args()` function.

***A reader class***
- **Class attributes** should be **the previously defined click options**.
- The class should have **a `read()` method**, yielding a stream object. This stream object can be chosen from [available stream classes](https://github.com/artefactory/nautilus-connectors-kit/tree/dev/nck/streams%29), and has **2 attributes: a stream name + a source generator function** named `result_generator()`, yielding individual source records.

The `nck/helpers/<SOURCE_NAME>_helper.py` should implement helper methods and configuration variables (*warning: we are planning to move configuration variables to a separate module for reasons of clarity*).

**2 -  In parallell, create unit tests for your methods under the `tests/` directory**

**3 - Add your click-decorated reader function to the `nck/readers/__init__.py` file**

**4 - Complete the documentation**
- Add your reader to [the list of existing readers](https://github.com/artefactory/nautilus-connectors-kit/blob/dev/README.md)
- Create dedicated documentation for your reader CLI command on [this Readme](https://github.com/artefactory/nautilus-connectors-kit/blob/dev/nck/readers/README.md). It should include  the followings sections: *Source API - How to obtain credentials - Quickstart - Command name - Command options*

### How to develop a new stream

*Streams are local objects used by writers to process individual records collected from the source.*

Each ***stream class*** should have:
 - **2 attributes : a stream name + a source generator function**. Both values will be passed by the associated reader class (*the generator function is the* `result_generator()` *function defined in the reader class*).
- **a `readlines()` method**, yielding individual source records.

Currently, these components are defined in the parent `Stream` class (*defined in the* `nck/streams/stream.py` *module*), and are inherited by all stream subclasses.

### How to develop a new writer

*Writers are writing the output stream object to the destination of your choice.*

To develop a new writer, you should:

**1 - Create the following module: `nck/writers/<DESTINATION_NAME>_writer.py`**

This module should implement 2 components:

***A click-decorated writer function***
 - The writer function should be **decorated with**: a `@click.command()` decorator, several `@click.option()` decorators (*one for each input that should be provided by end-users*) and a `@processor()` decorator (*preventing secrets to appear in logs*). For further information on how  to implement these decorators, please refer to [click documentation](https://click.palletsprojects.com/en/7.x/).
 - The writer function should return **a writer class** (*more details below*). A destination name prefix should be added to the name of each class attribute, using the `extract_args` function.

***A writer class***
- **Class attributes** should be **the previously defined click options**.
- The class should have **a `write()` method**, writing the stream object to the destination.

**3 - Add your click-decorated writer function to the `nck/writers/__init__.py` file**

**4 - Complete the documentation**
- Add your writer to [the list of existing writers](https://github.com/artefactory/nautilus-connectors-kit/blob/dev/README.md)
- Create dedicated documentation for your writer CLI command on [this Readme](https://github.com/artefactory/nautilus-connectors-kit/blob/dev/nck/writers/README.md). It should include  the followings sections: *Quickstart - Command name - Command options*

## To go further

#### Build a Docker image of the application and push it to GCP Container Registry

Update the values of the context variables featured in the .env module:
- `PROJECT_ID`: GCP Project ID
- `DOCKER_IMAGE`: image name
- `DOCKER_TAG`: tag name
- `DOCKER_REGISTRY`: registry hostname (e.g. `eu.gcr.io` for hosts located in the EU)

Build NCK image: `make build_base_image`
Push NCK image to GCP Container Registry: `make publish_base_image`

#### Package the application to use it as a binary or library

Build a wheel  for the NCK package (creates a `/dist` directory storing a <NCK_WHEEL>.whl file):
```
make dist
```
Build wheels for NCK dependencies (creates a `wheels/` directory storing multiple .whl files):
```
pip wheel --wheel-dir=wheels -r requirements.txt
```
Install the NCK package and its dependencies:
```
pip install --no-index --find-links=./wheels dist/<NCK_WHEEL>.whl
```
Then, you can use NCK as:
- A binary: `nckrun --help` (equivalent to `python nck/entrypoint.py --help`)
- A library: `from nck.readers.facebook_reader import FacebookReader`
