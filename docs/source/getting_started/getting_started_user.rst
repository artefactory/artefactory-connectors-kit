#########################
Getting started as a user
#########################

==================================
Set-up your developing environment
==================================

To start using ACK and/or contributing, first clone the `dev` branch of the `GitHub repository <https://github.com/artefactory/artefactory-connectors-kit/tree/dev>`__:

.. code-block:: shell

    git clone git@github.com:artefactory/artefactory-connectors-kit.git -b dev

-------------------
Virtual environment
-------------------

Create a virtual environment at the root of your local repository:

.. code-block:: shell

    python3 -m venv ack-env
    source ack-env/bin/activate

Install dependencies:

.. code-block:: shell

    pip install -r requirements.txt

=============================
Launch your first ACK command
=============================

Once this preliminary set-up is finalized, you can start using the application.

There is two different way to use ACK commands. You can either build a full command by passing every argument you want or build a .json config file and pass it to ACK. Both ways are described below.

---------------------
ACK full command line
---------------------

ACK commands can be broken down into 3 parts:

1. An entrypoint: all ACK cli commands are launched through the ``ack/entrypoints/cli/main.py`` executable.

.. code-block:: shell

    python ack/entrypoints/cli/main.py

2. A reader command, and its options: in the below example, we are reading Google Analytics data for the view <VIEW_ID>, retrieving sessions, pageviews and bounces by date from 2020-01-01 to 2020-01-03.

.. code-block:: shell

    read_ga --ga-client-id <CLIENT_ID> --ga-client-secret <CLIENT_SECRET> --ga-view-id <VIEW_ID> --ga-refresh-token <REFRESH_TOKEN> --ga-dimension ga:date --ga-metric ga:sessions --ga-metric ga:pageviews --ga-metric ga:bounces --ga-start-date 2020-01-01 --ga-end-date 2020-01-03

3. A writer command, and its options: in the below example, we are writing the output .nsjon stream into a Google Cloud Storage blob named ``google_analytics_report_2020-01-01.njson``, located under the Google Cloud Storage bucket ``ack_extracts``, with the path ``FR/google_analytics/``.

.. code-block:: shell

    write_gcs --gcs-project-id <GCP_PROJECT_ID> --gcs-bucket ack_extracts --gcs-prefix FR/google_analytics --gcs-filename google_analytics_report_2020-01-01.njson

To execute the ACK command as a whole, we just have to put these 3 parts together.

To simplify your first test, instead of the writer command ``write_gcs``, we recommend you to use ``write_console`` (*it will write output stream records into your terminal*) or ``write_local --local-directory <PATH_TO_DESTINATION>`` (*it will write output stream records into a local file*). In practice, these writer commands are very convenient for debugging, as they are quite simple.

In the end, if we use ``write_console`` as a writer command, the combined ACK command will be:

.. code-block:: shell

    python ack/entrypoints/cli/main.py read_ga --ga-client-id <CLIENT_ID> --ga-client-secret <CLIENT_SECRET> --ga-view-id <VIEW_ID> --ga-refresh-token <REFRESH_TOKEN> --ga-dimension ga:date --ga-metric sessions --ga-metric ga:pageviews --ga-metric ga:bounces --ga-start-date 2020-01-01 --ga-end-date 2020-01-03 write_console

You can now execute it into your terminal.

.. _ackwithjson:

----------------------------
ACK with a .json config file
----------------------------

ACK can also use a .json config file to get all arguments. You can broke this command in 3 parts:

1. An entrypoint: all ACK commands are launched through the ``ack/entrypoints/json/main.py`` executable.

.. code-block:: shell

    python ack/entrypoints/json/main.py

2. A path argument ``--config-file`` that will give to the entrypoint where to find the .json file with all the information.

3. A .json config file organized as followed, with one reader and at least one writer:

.. code-block:: JSON

    {
      "option_name": "value",
      "reader": {
        "name": "reader_name",
        "option_name": "value",
        "option_name": ["value1", "value2"],
      },
      "writers": [
        {
          "name": "writer_name",
          "option_name": "value",
        },
      ]
    }

Here is a good example of a .json config file:

.. code-block:: JSON

    {
      "reader": {
        "name": "twitter",
        "consumer_key": "****",
        "consumer_secret": "****",
        "access_token": "****",
        "access_token_secret": "*****",
        "account_id": "*****",
        "report_type": "ANALYTICS",
        "entity": "PROMOTED_TWEET",
        "metric_group": ["ENGAGEMENT"],
        "segmentation_type": "AGE",
        "granularity": "DAY",
        "start_date": "2021-02-25",
        "end_date": "2021-03-04"
      },
      "writers": [
        {
          "name": "console"
        }
      ]
    }

**Now that you understand how ACK commands are structured, you can follow these links to find the full documentation on available** :ref:`readers:Readers` and :ref:`writers:Writers`.

=====================
Normalize field names
=====================

Some destinations have specific requirements for field names. This is the case of BigQuery, that only accepts letters, digits and underscores.

To normalize field names (i.e. replace any special character or white space by an underscore), you can add the option ``--normalize-keys true`` between ``python ack/entrypoint.py`` and the invocated reader command. If we keep using the previous Google Analytics example, it would give:

.. code-block:: shell

    python ack/entrypoints/cli/main.py --normalize-keys true read_ga --ga-client-id <CLIENT_ID> --ga-client-secret <CLIENT_SECRET> --ga-view-id <VIEW_ID> --ga-refresh-token <REFRESH_TOKEN> --ga-dimension ga:date --ga-metric sessions --ga-metric ga:pageviews --ga-metric ga:bounces --ga-start-date 2020-01-01 --ga-end-date 2020-01-03 write_console
