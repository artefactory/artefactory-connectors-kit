#######
Writers
#######

**Writers are writing output stream records to the destination of your choice.**

*About to develop a new writer?* See the :ref:`getting_started:How to develop a new writer` section.

*Just want to use an existing writer?* This page provides you with documentation on available commands:

================
Amazon S3 Writer
================

----------
Quickstart
----------

The following command would allow you to:

- write output stream records to a blob named ``google_analytics_report_2020-01-01.njson``
- under the Amazon S3 bucket ``ack_extracts``
- organized according to the following path: ``ack_extracts/FR/google_analytics/google_analytics_report_2020-01-01.njson``

.. code-block:: shell

    write_s3 --s3-bucket-name ack_extracts --s3-prefix FR/google_analytics --s3-filename google_analytics_report_2020-01-01.njson --s3-bucket-region <BUCKET_REGION> --s3-access-key-id <ACCESS_KEY_ID> --s3-access-key-secret <ACCESS_KEY_SECRET>

------------
Command name
------------

CMD: ``write_s3``

JSON: ``amazon_s3``

---------------
Command options
---------------

==============================  ======================  ==============================
CMD Options                     JSON Options            Definition
==============================  ======================  ==============================
``--s3-bucket-name``            ``bucket_name``         S3 bucket name
``--s3-prefix``                 ``prefix``              S3 blob prefix
``--s3-filename``               ``filename``            S3 blob name
``--s3-bucket-region``          ``bucket_region``       S3 bucket region
``--s3-access-key-id``          ``access_key_id``       S3 access key ID
``--s3-access-key-secret``      ``access_key_secret``   S3 access key secret
==============================  ======================  ==============================

======================
Google BigQuery Writer
======================

----------
Quickstart
----------

The following command would allow you to:

- store output stream records into the BigQuery table ``google_analytics``
- located under the BigQuery dataset ``ack``

As a preliminary step, stream data would be uploaded into a temporary blob located under the Cloud Storage bucket ``ack_extracts``.

.. code-block:: shell

    write bq --bq-dataset ack --bq-table google_analytics --bq-bucket ack-extracts

------------
Command name
------------

CMD: ``write_bq``

JSON: ``google_bigquery``

---------------
Command options
---------------

==============================  ======================  =================================================================================================================================================
CMD Options                     JSON Options            Definition
==============================  ======================  =================================================================================================================================================
``--bq-dataset``                ``dataset``             BigQuery dataset name
``--bq-table``                  ``table``               BigQuery table name
``--bq-write-disposition``      ``write-disposition``   BigQuery write disposition. Possible values: TRUNCATE (default), APPEND
``--bq-partition-column``       ``partition-column``    (Optional) Field to be used as a partition column (more information on `this page <https://cloud.google.com/bigquery/docs/partitioned-tables>`__)
``--bq-location``               ``location``            BigQuery dataset location. Possible values: EU (default), US.
``--bq-bucket``                 ``bucket``              Cloud Storage bucket in which stream data should be written as a first step, before being uploaded into the BigQuery destination table
``--bq-keep-files``             ``keep-files``          False (default) if Cloud Storage blob should be deleted once the data has been uploaded into the BigQuery destination table, True otherwise
==============================  ======================  =================================================================================================================================================

===========================
Google Cloud Storage Writer
===========================

----------
Quickstart
----------

The following command would allow you to:

- write output stream records to a blob named ``google_analytics_report_2020-01-01.njson``
- located under the Cloud Storage bucket ``ack_extracts``
- organized according to the following path: ``ack_extracts/FR/google_analytics/google_analytics_report_2020-01-01.njson``

.. code-block:: shell

    write_gcs --gcs-project-id <GCP_PROJECT_ID> --gcs-bucket ack_extracts --gcs-prefix FR/google_analytics --gcs-filename google_analytics_report_2020-01-01.njson

------------
Command name
------------

CMD: ``write_gcs``

JSON: ``google_cloud_storage``

---------------
Command options
---------------

==============================  ===============  ==============================
CMD Options                     JSON Options     Definition
==============================  ===============  ==============================
``--gcs-project-id``            ``project_id``   GCP project ID
``--gcs-bucket``                ``bucket``       Cloud Storage bucket name
``--gcs-prefix``                ``prefix``       Cloud Storage blob prefix
``--gcs-file-name``             ``file_name``    Cloud Storage blob name
==============================  ===============  ==============================

=========================
Azure Blob Storage Writer
=========================

----------
Quickstart
----------

The following command would allow you to:

- write output stream records to a blob named ``azure_report_2020-01-01.njson``
- located under the container ``ack_extracts``
- organized according to the following path: ``ack_extracts/FR/analytics/azure_report_2020-01-01.njson``

.. code-block:: shell

    write_azure_blob --azure-blob-connection-string <CONNECTION_STRING> --azure-blob-container ack_extracts --azure-prefix FR/analytics --gcs-filename azure_report_2020-01-01.njson

------------
Command name
------------

CMD: ``write_azure_blob``

JSON: ``azure_blob_storage``

---------------
Command options
---------------

====================================  ======================  =====================================================================================================================
CMD Options                           JSON Options            Definition
====================================  ======================  =====================================================================================================================
``--azure-blob-connection-string``    ``connection_string``   Azure connection string, if not given it will try to get the environment variable 'AZURE_STORAGE_CONNECTION_STRING'
``--azure-blob-container``            ``container``           Azure Storage container name
``--azure-blob-prefix``               ``prefix``              Azure Storage blob prefix
``--azure-blob-filename``             ``filename``            Azure Storage blob name
====================================  ======================  =====================================================================================================================

============
Local Writer
============

----------
Quickstart
----------

The following command would allow you to write a file ``google_analytics_report_2020-01-01.njson`` on the ``~/Desktop`` directory of your local machine:

.. code-block:: shell

    write_local --local-directory ~/Desktop/ --local-file-name google_analytics_report_2020-01-01.njson

------------
Command name
------------

CMD: ``write_local``

JSON: ``local``

---------------
Command options
---------------

==============================  ==============  ===============================================================
CMD Options                     JSON Options    Definition
==============================  ==============  ===============================================================
``--local-directory (-d)``      ``directory``   Directory in which the file should be stored
``--local-file-name (-n)``      ``file_name``   File name
==============================  ==============  ===============================================================

==============
Console Writer
==============

----------
Quickstart
----------

The following command would allow you to write stream output records directly into your terminal, which is very convenient for debugging:

.. code-block:: shell

    write_console

------------
Command name
------------

CMD: ``write_console``

JSON: ``console``

---------------
Command options
---------------
*This writer command expects no options.*
