#############
To go further
#############

=============================================================================
Build a Docker image of the application and push it to GCP Container Registry
=============================================================================

Update the values of the context variables featured in the .env module:

- ``PROJECT_ID``: GCP Project ID
- ``DOCKER_IMAGE``: image name
- ``DOCKER_TAG``: tag name
- ``DOCKER_REGISTRY``: registry hostname (e.g. eu.gcr.io for hosts located in the EU)

Build NCK image:

.. code-block:: shell

    make build_base_image

Push NCK image to GCP Container Registry:

.. code-block:: shell

    make publish_base_image

========================================================
Package the application to use it as a binary or library
========================================================

Build a wheel for the NCK package (creates a ``/dist`` directory storing a <NCK_WHEEL>.whl file):

.. code-block:: shell

    make dist

Build wheels for NCK dependencies (creates a ``wheels/`` directory storing multiple .whl files):

.. code-block:: shell

    pip wheel --wheel-dir=wheels -r requirements.txt

Install the NCK package and its dependencies:

.. code-block:: shell

    pip install --no-index --find-links=./wheels dist/<NCK_WHEEL>.whl

Then, you can use NCK as:

- A binary: ``nckrun --help`` (equivalent to ``python nck/entrypoint.py --help``)
- A library: ``from nck.readers.facebook_reader import FacebookReader``
