###############
Getting started
###############

==================================
Set-up your developing environment
==================================

To start using NCK and/or contributing, first clone the `dev` branch of the `GitHub repository <https://github.com/artefactory/nautilus-connectors-kit/tree/dev>`__:

.. code-block:: shell

    git clone git@github.com:artefactory/nautilus-connectors-kit.git -b dev

-------------------
Virtual environment
-------------------

Create a virtual environment at the root of your local repository:

.. code-block:: shell

    python3 -m venv nck-env
    source nck-env/bin/activate

Install dependencies:

.. code-block:: shell

    pip install -r requirements.txt
    pip install -r requirements-dev.text

-------
Linting
-------

We are using `black <https://pypi.org/project/black/>`__ and `Flake8 <https://flake8.pycqa.org/en/latest/>`__ for code linting.

The black and Flake8 packages have already been installed in your virtual environment with dependencies. Also, a Flake8 configuration file (``.flake8``) and a black configuration file (``pyproject.toml``) are available at the root at this repository.

----------------
Pre-commit hooks
----------------

We are using `pre-commit <https://pre-commit.com/>`__ hooks to point out linting issues in our code before submission to code review.

The pre-commit package has already been installed in your virtual environment with dependencies. Also, a pre-commit configuration file (``.pre-commit-config.yaml``) is available at the root of this repository.

To finalize the installation and install git hooks scripts, execute:

.. code-block:: shell

    pre-commit install

For now on, the ``pre-commit`` command will run automatically on every ``git commit``.

-------------------------------
TDD (*Test-Driven Development*)
-------------------------------

We are running tests using `nose <https://nose.readthedocs.io/en/latest/usage.html>`__, an extension of the Python `unittest <https://docs.python.org/fr/3/library/unittest.html>`__ framework.

The nose package has already been installed in your virtual environment with dependencies.
To run existing tests, execute:

.. code-block:: shell

    nosetests

-------------
Documentation
-------------

We are using `Sphinx <https://www.sphinx-doc.org/en/master/>`__ with a ReadTheDocs theme to document the application.

The Sphinx package has already been installed in your virtual environment with dependencies.

Sphinx documentation is available under the ``docs/source/`` directory of the `GitHub repository <https://github.com/artefactory/nautilus-connectors-kit/tree/dev>`__ as .rst files (each file representing a page).
It uses the reStructuredText (reST) syntax: to learn more about it, see the `official documentation <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`__.

You can modify existing pages by editing the corresponding .rst files.

If you want to create a new page, you should:

1. Create a new ``<YOUR_PAGE_NAME>.rst`` file under the ``docs/source/`` directory
2. Add a ``./<YOUR_PAGE_NAME>.rst`` line in the ``docs/source/index.rst`` file as follows:

.. code-block:: yaml

    .. toctree::
       :maxdepth: 2
       caption: Contents:

       ./overview.rst
       ./getting_started.rst
       ./readers.rst
       ./streams.rst
       ./writers.rst
       ./to_go_further.rst
       ./<YOUR_PAGE_NAME>.rst

To preview your changes, execute:

.. code-block:: shell

    cd docs/
    make html

It will create the .html files corresponding to your .rst source files in the ``docs/build/`` directory.
You can launch a preview of these .html files in your brower with your code editor (with VSCode: right-click on any .html file > Open with Live Server).

Sphinx documentation is automatically deployed on GitHub Pages (by a dedicated GitHub workflow) each time code is pushed to the 'dev' branch of the repository.

=============================
Launch your first NCK command
=============================

Once this preliminary set-up is finalized, you can start using the application.

NCK commands can be broken down into 3 parts:

1. An entrypoint: all NCK commands are launched through the ``nck/entrypoint/entrypoint.py`` executable.

.. code-block:: shell

    python nck/entrypoint/entrypoint.py

2. A reader command, and its options: in the below example, we are reading Google Analytics data for the view <VIEW_ID>, retrieving sessions, pageviews and bounces by date from 2020-01-01 to 2020-01-03.

.. code-block:: shell

    read_ga --ga-client-id <CLIENT_ID> --ga-client-secret <CLIENT_SECRET> --ga-view-id <VIEW_ID> --ga-refresh-token <REFRESH_TOKEN> --ga-dimension ga:date --ga-metric ga:sessions --ga-metric ga:pageviews --ga-metric ga:bounces --ga-start-date 2020-01-01 --ga-end-date 2020-01-03

3. A writer command, and its options: in the below example, we are writing the output .nsjon stream into a Google Cloud Storage blob named ``google_analytics_report_2020-01-01.njson``, located under the Google Cloud Storage bucket ``nck_extracts``, with the path ``FR/google_analytics/``.

.. code-block:: shell

    write_gcs --gcs-project-id <GCP_PROJECT_ID> --gcs-bucket nck_extracts --gcs-prefix FR/google_analytics --gcs-filename google_analytics_report_2020-01-01.njson

To execute the NCK command as a whole, we just have to put these 3 parts together.

To simplify your first test, instead of the writer command ``write_gcs``, we recommend you to use ``write_console`` (*it will write output stream records into your terminal*) or ``write_local --local-directory <PATH_TO_DESTINATION>`` (*it will write output stream records into a local file*). In practice, these writer commands are very convenient for debugging, as they are quite simple.

In the end, if we use ``write_console`` as a writer command, the combined NCK command will be:

.. code-block:: shell

    python nck/entrypoint/entrypoint.py read_ga --ga-client-id <CLIENT_ID> --ga-client-secret <CLIENT_SECRET> --ga-view-id <VIEW_ID> --ga-refresh-token <REFRESH_TOKEN> --ga-dimension ga:date --ga-metric sessions --ga-metric ga:pageviews --ga-metric ga:bounces --ga-start-date 2020-01-01 --ga-end-date 2020-01-03 write_console

You can now execute it into your terminal.

**Now that you understand how NCK commands are structured, you can follow these links to find the full documentation on available** :ref:`readers:Readers` and :ref:`writers:Writers`.

=====================
Normalize field names
=====================

Some destinations have specific requirements for field names. This is the case of BigQuery, that only accepts letters, digits and underscores.

To normalize field names (i.e. replace any special character or white space by an underscore), you can add the option ``--normalize-keys true`` between ``python nck/entrypoint/entrypoint.py`` and the invocated reader command. If we keep using the previous Google Analytics example, it would give:

.. code-block:: shell

    python nck/entrypoint/entrypoint.py --normalize-keys true read_ga --ga-client-id <CLIENT_ID> --ga-client-secret <CLIENT_SECRET> --ga-view-id <VIEW_ID> --ga-refresh-token <REFRESH_TOKEN> --ga-dimension ga:date --ga-metric sessions --ga-metric ga:pageviews --ga-metric ga:bounces --ga-start-date 2020-01-01 --ga-end-date 2020-01-03 write_console

==========
Contribute
==========

NCK is an open-source application initially developed by Artefact team: feel free to contribute!

You can find open issues on `this GitHub page <https://github.com/artefactory/nautilus-connectors-kit/issues>`__. If you identify additional enhancements/fixes that could be beneficial to the application, don't hesitate to add them to the list.

Here are a few tips/guidelines to help you efficiently contribute:

---------------------------
How to develop a new reader
---------------------------

*Readers are reading data from an API source, and transform it into a stream object.*

To create a new reader, you should:

1. Create a ``nck/readers/<SOURCE_NAME>/`` directory, having the following structure:

.. code-block:: shell

    - nck/
    -- readers/
    --- <SOURCE_NAME>/
    ---- cli.py
    ---- reader.py
    ---- helper.py # Optional
    ---- config.py # Optional

``cli.py``

This module should implement a click-decorated reader function:

  - The reader function should be decorated with: a ``@click.command()`` decorator, several ``@click.option()`` decorators (*one for each input provided by end-users*) and a ``@processor()`` decorator (*preventing secrets to appear in logs*). For further information on how to implement these decorators, please refer to `click documentation <https://click.palletsprojects.com/en/7.x/>`__.
  - The reader function should return a reader class (*more details below*). The source prefix of each option will be removed when passed to the writer class, using the ``extract_args()`` function.

``reader.py``

This module should implement a reader class:

  - Class attributes should be the previously defined click options.
  - The class should have a ``read()`` method, yielding a stream object. This stream object can be chosen from `available stream classes <https://github.com/artefactory/nautilus-connectors-kit/tree/dev/nck/streams>`__, and has 2 attributes: a stream name and a source generator function named ``result_generator()``, yielding individual source records.

``helper.py`` (Optional)

This module gathers all helper functions used in the ``reader.py`` module.

``config.py`` (Optional)

This module gathers all configuration variables.

2. In parallell, create unit tests for your methods under the ``tests/`` directory

3. Add your click-decorated reader function to the ``nck/readers/__init__.py`` file

4. Complete the documentation:

    - Add your reader to the list of existing readers in the :ref:`overview:Available Connectors` section.
    - Add your reader to the list of existing readers in the repo's ``./README.md``.
    - Create dedicated documentation for your reader CLI command on the :ref:`readers:Readers` page. It should include the followings sections: *Source API - How to obtain credentials - Quickstart - Command name - Command options*

---------------------------
How to develop a new stream
---------------------------

*Streams are local objects used by writers to process individual records collected from the source.*

Each stream class should have:

- 2 attributes : a stream name and a source generator function. Both values will be passed by the associated reader class (*the generator function is the* ``result_generator()`` *function defined in the reader class*).
- a ``readlines()`` method, yielding individual source records.

Currently, these components are defined in the parent ``Stream`` class (*defined in the* ``nck/streams/stream.py`` *module*), and are inherited by all stream subclasses.

---------------------------
How to develop a new writer
---------------------------

*Writers are writing the output stream object to the destination of your choice.*

To develop a new writer, you should:

1. Create a ``nck/writers/<DESTINATION_NAME>/`` directory, having the following structure:

.. code-block:: shell

    - nck/
    -- writers/
    --- <DESTINATION_NAME>/
    ---- cli.py
    ---- writer.py
    ---- helper.py # Optional
    ---- config.py # Optional

``cli.py``

This module should implement a click-decorated writer function:

  - The writer function should be decorated with: a ``@click.command()`` decorator, several ``@click.option()`` decorators (*one for each input provided by end-users*) and a ``@processor()`` decorator (*preventing secrets to appear in logs*). For further information on how to implement these decorators, please refer to `click documentation <https://click.palletsprojects.com/en/7.x/>`__.
  - The writer function should return a writer class (*more details below*). The destination prefix of each option will be removed when passed to the writer class, using the ``extract_args()`` function.

``writer.py``

This module should implement a writer class:

  - Class attributes should be the previously defined click options.
  - The class should have a ``write()`` method, writing the stream object to the destination.

``helper.py`` (Optional)

This module gathers all helper functions used in the ``writer.py`` module.

``config.py`` (Optional)

This module gathers all configuration variables.

2. In parallell, create unit tests for your methods under the ``tests/`` directory

3. Add your click-decorated writer function to the ``nck/writers/__init__.py`` file

4. Complete the documentation:

    - Add your writer to the list of existing writers in the :ref:`overview:Available Connectors` section.
    - Add your reader to the list of existing readers in the repo's ``./README.md``.
    - Create dedicated documentation for your writer CLI command on the :ref:`writers:Writers` page. It should include the followings sections: *Quickstart - Command name - Command options*
