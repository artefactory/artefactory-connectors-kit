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

Build ACK image:

.. code-block:: shell

    make build_base_image

Push ACK image to GCP Container Registry:

.. code-block:: shell

    make publish_base_image
