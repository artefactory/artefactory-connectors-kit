#######
Readers
#######

**Readers are reading data from an API source, and transform it into a stream object.**

*About to develop a new reader?* See the :ref:`getting_started:How to develop a new reader` section.

*Just want to use an existing reader?* This page provides you with documentation on available commands:

=======================
Adobe Analytics Readers
=======================

As of May 2020 (last update of this section of the documentation), **two versions of Adobe Analytics Reporting API are  coexisting: 1.4 and 2.0**. As some functionalities of API 1.4 have not been made available in API 2.0 yet (Data Warehouse reports in particular), our Adobe Analytics Readers are also available in these two versions.

-------------------------
How to obtain credentials
-------------------------

Both Adobe Analytics Readers use the **JWT authentication framework**.

- Get developer access to Adobe Analytics (documentation can be found `here <https://helpx.adobe.com/enterprise/using/manage-developers.html>`__)
- Create a Service Account integration to Adobe Analytics on `Adobe Developer Console <https://console.adobe.io/>`__
- Use the generated JWT credentials (Client ID, Client Secret, Technical Account ID, Organization ID and private.key file) to retrieve your Global Company ID (to be requested to `Discovery API <https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/discovery.md>`__). All these parameters will be passed to Adobe Analytics Readers.

==========================
Adobe Analytics Reader 1.4
==========================

----------
Source API
----------

`Analytics API v1.4 <https://github.com/AdobeDocs/analytics-1.4-apis>`__

----------
Quickstart
----------

Call example to Adobe Analytics Reader 1.4, getting the number of visits per day and tracking code for a specified Report Suite, between 2020-01-01 and 2020-01-31:

.. code-block:: shell

    python nck/entrypoint.py read_adobe --adobe-client-id <CLIENT_ID> --adobe-client-secret <CLIENT_SECRET> --adobe-tech-account-id <TECH_ACCOUNT_ID> --adobe-org-id <ORG_ID> --adobe-private-key <PRIVATE_KEY> --adobe-global-company-id <GLOBAL_COMPANY_ID> --adobe-report-suite-id <REPORT_SUITE_ID> --adobe-date-granularity day --adobe-report-element-id trackingcode --adobe-report-metric-id visits --adobe-start-date 2020-01-01 --adobe-end-date 2020-01-31 write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_adobe``

---------------
Command options
---------------

==============================  =================================================================================================================================================================================
Options                         Definition
==============================  =================================================================================================================================================================================
``--adobe-client-id``           Client ID, that you can find on Adobe Developer Console
``--adobe-client-secret``       Client Secret, that you can find on Adobe Developer Console
``--adobe-tech-account-id``     Technical Account ID, that you can find on Adobe Developer Console
``--adobe-org-id``              Organization ID, that you can find on Adobe Developer Console
``--adobe-private-key``         Content of the private.key file, that you had to provide to create the integration. Make sure to enter the parameter in quotes, include headers, and indicate newlines as ``\n``.
``--adobe-global-company-id``   Global Company ID (to be requested to `Discovery API <https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/discovery.md>`__)
``--adobe-list-report-suite``   Should be set to True if you wish to request the list of available Adobe Report Suites (default: False). If set to True, the below parameters should be left empty.
``--adobe-report-suite-id``     ID of the requested Adobe Report Suite
``--adobe-report-element-id``   ID of the element (i.e. dimension) to include in the report
``--adobe-report-metric-id``    ID of the metric to include in the report
``--adobe-date-granularity``    Granularity of the report. Possible values: PREVIOUS_DAY, LAST_30_DAYS, LAST_7_DAYS, LAST_90_DAYS
``--adobe-start-date``          Start date of the period to request (format: YYYY-MM-DD)
``--adobe-end-date``            End date of the period to request (format: YYYY-MM-DD)
==============================  =================================================================================================================================================================================

---------------------
Addtional information
---------------------

- **The full list of available elements and metrics** can be retrieved with the `GetElements <https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/reporting-api/methods/r_GetElements.md>`__ and `GetMetrics <https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/reporting-api/methods/r_GetMetrics.md>`__ methods.
- **Adobe Analytics Reader 1.4 requests Data Warehouse reports** (the "source" parameter is set to "warehouse" in the report description), allowing it to efficiently process multiple-dimension requests.
- **If you need further information**, the documentation of Adobe APIs 1.4 can be found `here <https://github.com/AdobeDocs/analytics-1.4-apis>`__.

==========================
Adobe Analytics Reader 2.0
==========================

----------
Source API
----------

`Analytics API v2.0 <https://github.com/AdobeDocs/analytics-2.0-apis>`__

----------
Quickstart
----------

Call example to Adobe Analytics Reader 2.0, getting the number of visits per day and tracking code for a specified Report Suite, between 2020-01-01 and 2020-01-31:

.. code-block:: shell

    python nck/entrypoint.py read_adobe_2_0 --adobe-2-0-client-id <CLIENT_ID> --adobe-2-0-client-secret <CLIENT_SECRET> --adobe-2-0-tech-account-id <TECH_ACCOUNT_ID> --adobe-2-0-org-id <ORG_ID> --adobe-2-0-private-key <PRIVATE_KEY> --adobe-2-0-global-company-id <GLOBAL_COMPANY_ID> --adobe-2-0-report-suite-id <REPORT_SUITE_ID> --adobe-2-0-dimension daterangeday --adobe-2-0-dimension campaign --adobe-2-0-start-date 2020-01-01 --adobe-2-0-end-date 2020-01-31 --adobe-2-0-metric visits write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_adobe_2_0``

---------------
Command options
---------------

==================================  =================================================================================================================================================================================
Options                             Definition
==================================  =================================================================================================================================================================================
``--adobe-2-0-client-id``           Client ID, that you can find on Adobe Developer Console
``--adobe-2-0-client-secret``       Client Secret, that you can find on Adobe Developer Console
``--adobe-2-0-tech-account-id``     Technical Account ID, that you can find on Adobe Developer Console
``--adobe-2-0-org-id``              Organization ID, that you can find on Adobe Developer Console
``--adobe-2-0-private-key``         Content of the private.key file, that you had to provide to create the integration. Make sure to enter the parameter in quotes, include headers, and indicate newlines as ``\n``.
``--adobe-2-0-global-company-id``   Global Company ID (to be requested to `Discovery API <https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/discovery.md>`__)
``--adobe-2-0-report-suite-id``     ID of the requested Adobe Report Suite
``--adobe-2-0-dimension``           Dimension to include in the report
``--adobe-2-0-metric``              Metric to include in the report
``--adobe-2-0-start-date``          Start date of the period to request (format: YYYY-MM-DD)
``--adobe-2-0-end-date``            Start date of the period to request (format: YYYY-MM-DD)
``--adobe-2-0-date-range``          Date range. By default, not available in Adobe, so choose among NCK default values: YESTERDAY, LAST_7_DAYS, PREVIOUS_WEEK, PREVIOUS_MONTH, LAST_90_DAYS
==================================  =================================================================================================================================================================================

----------------------
Additional information
----------------------

- **In API 2.0, dimension and metric names are slightly different from API 1.4**. To get new metric and dimension names and reproduce the behavior of Adobe Analytics UI as closely as possible, `enable the Debugger feature in Adobe Analytics Workspace <https://github.com/AdobeDocs/analytics-2.0-apis/blob/master/reporting-tricks.md>`__: it allow you to visualize the back-end JSON requests made by Adobe Analytics UI to Reporting API 2.0.
- **In API 2.0, the date granularity parameter was removed, and should now be handled as a dimension**: a request featuring ``--adobe-dimension daterangeday`` will produce a report with a day granularity.
- **API 2.0 does not feature Data Warehouse reports yet** (along with other features, that are indicated on the "Current limitations" section of `this page <https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/migration-guide.md>`__). For this reason, if you wish to collect multiple-dimension reports, Adobe Analytics Reader 1.4 might be a more efficient solution in terms of processing time. 
- **If you need any further information**, the documentation of Adobe APIs 2.0 can be found `here <https://github.com/AdobeDocs/analytics-2.0-apis>`__.

================
Amazon S3 Reader
================

----------
Source API
----------

`AWS SDK for Python (Boto3) <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>`__

----------
Quickstart
----------

Execute the following commands to set your credentials:

.. code-block:: shell

    export REGION_NAME=<S3 bucket region>
    export AWS_ACCESS_KEY_ID=<S3 access key ID>
    export AWS_SECRET_ACCESS_KEY=<S3 access key secret>

Once done, launch your S3 reader command. The following command retrieves the blobs located under the Amazon S3 bucket ``daily_reports`` and the blob prefix ``FR/offline_sales/``.

.. code-block:: shell

    python nck/entrypoint.py read_s3 --s3-bucket daily_reports --s3-prefix FR/offline_sales --s3-format csv write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_s3``

---------------
Command options
---------------

==============================  =======================================================================================================================================================================================================================================================================================================================================================================================================================
Options                         Definition
==============================  =======================================================================================================================================================================================================================================================================================================================================================================================================================
``--s3-bucket``                 S3 bucket name
``--s3-prefix``                 S3 blob prefix. Several prefixes can be provided in a single command.
``--s3-format``                 S3 blob format. Possible values: csv, gz.
``--s3-dest-key-split``         Indicates how to retrieve a blob name from a blob key (a blob key being the combination of a blob prefix and a blob name: <BLOB_PREFIX>/<BLOB_NAME>). The reader splits the blob key on the "/" character: the last element of the output list is considered as the blob name, and is used to name the stream produced by the reader. This option defines how many splits to do. Default: -1 (split on all occurences).
``--s3-csv-delimiter``          Delimiter that should be used to read the .csv file. Default: ,
``--s3-csv-fieldnames``         List of field names. If set to None (default), the values in the first row of .csv file will be used as field names.
==============================  =======================================================================================================================================================================================================================================================================================================================================================================================================================

=================
Confluence Reader
=================

----------
Source API
----------

`Confluence Cloud REST API <https://developer.atlassian.com/cloud/confluence/rest/intro/>`__

----------
Quickstart
----------

The Confluence Reader handles calls to the **Get Content endpoint** of Confluence Cloud REST API.

The following command retrieves the titles, space names, tiny links and label names of all pages located under the Atlassian domain <ATLASSIAN_DOMAIN>, filtered on the spacekeys <KEY_1> and <KEY_2>.

.. code-block:: shell

    python nck/entrypoint.py read_confluence --confluence-user-login <USER_LOGIN> --confluence-api-token <API_TOKEN> --confluence-atlassian-domain <ATLASSIAN_DOMAIN> --confluence-content-type "page" --confluence-field "title" --confluence-field "space.name" --confluence-field "tiny_link" --confluence-field "label_names" --confluence-spacekey <KEY_1> --confluence-spacekey <KEY_2> write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_confluence``

---------------
Command options
---------------

==================================  ============================================================================================================================================================================================
Options                             Definition
==================================  ============================================================================================================================================================================================
``--confluence-user-login``         User login associated with your Atlassian account
``--confluence-api-token``          API token associated with your Atlassian account (can be generated on `this page <https://id.atlassian.com/manage-profile/security/api-tokens>`__)
``--confluence-atlassian-domain``   Atlassian domain under which the content to request is located
``--confluence-content-type``       Type of content on which the report should be filtered. Possible values: page (default), blog_post.
``--confluence-spacekey``           (Optional) Space keys on which the report should be filtered
``--confluence-field``              Fields that should be included in the report (path.to.field.value or custom_field)
``--confluence-normalize-stream``   If set to True, yields a NormalizedJSONStream (spaces and special characters replaced by '_' in field names, which is useful for BigQuery). Else (default), yields a standard JSONStream.
==================================  ============================================================================================================================================================================================

Please visit the following two pages for a better understanding of the `Authentification method <https://developer.atlassian.com/cloud/confluence/basic-auth-for-rest-apis/>`__, and of the parameters used in the `Get Content endpoint <https://developer.atlassian.com/cloud/confluence/rest/api-group-content/#api-api-content-get>`__.

The Confluence Reader supports two types of fields:

**Standard fields** - You specify the path to the value that you you wish to retrieve in the raw API response (each path item being separated by dots).

*Example* - The standard field ``space.name`` will retrieve the value ``"How To Guides"`` for the first item, and the value  ``"Clients"`` for the second item.

.. code-block:: shell

    RAW_API_RESPONSE = {"results":
        [
            {
                "title": "Making API requests with NCK",
                "space": {"name": "How To Guides"},
                "metadata": {"labels": {"results": [{"name": "nck"}, {"name": "api"}]}}
            },
            {
                "title": "Samsung - Precision Marketing",
                "space": {"name": "Clients"},
                "metadata": {"labels": {"results": [{"name": "pm"}]}}
            }
        ]
    }

**Custom fields** - If the format of the raw API response does not match your needs, you can define a custom field. Available custom fields are described in the CUSTOM_FIELDS variable of the ``nck.helpers.confluence_helper`` module.

*Example* - The custom field ``label_names`` transforms the value of the source field ``metadata.labels.results`` using the function ``_get_key_values_from_list_of_dct``. In other words, using the first record of the previous example, it will format ``[{"name": "nck"}, {"name": "api"}]`` into ``"nck|api"``.

.. code-block:: shell

    CUSTOM_FIELDS = {
        "label_names": {
        "source_field": "metadata.labels.results",
        "format_function": _get_key_values_from_list_of_dct,
        "format_function_kwargs": {"key": "name"},
        "formatted_object_type": str
        }
    }

=========================
Facebook Marketing Reader
=========================

----------
Source API
----------

`Facebook Marketing API <https://developers.facebook.com/docs/marketing-api/reference/v7.0>`__

----------
Quickstart
----------

The Facebook Marketing Reader handles calls to 2 endpoints of the Facebook Marketing API: **Facebook Ad Insights** (to retrieve performance data), and **Facebook Ad Management** (to retrieve configuration data).

*Example of Ad Insights Request*

.. code-block:: shell

    python nck/entrypoint.py read_facebook --facebook-access-token <ACCESS_TOKEN> --facebook-object-id <OBJECT_ID> --facebook-breakdown age --facebook-breakdown gender --facebook-action-breakdown action_type --facebook-field ad_id --facebook-field ad_name --facebook-field impressions --facebook-field clicks --facebook-field actions[action_type:post_engagement] --facebook-field actions[action_type:video_view] --facebook-field age --facebook-field gender --facebook-time-increment 1 --facebook-start-date 2020-01-01 --facebook-end-date 2020-01-03 write_console

*Example of Ad Management Request*

.. code-block:: shell

    python nck/entrypoint.py read_facebook --facebook-access-token <ACCESS_TOKEN> --facebook-object-id <OBJECT_ID>  --facebook-ad-insights False --facebook-level ad --facebook-field id --facebook-field creative[id] --facebook-add-date-to-report True --facebook-start-date 2020-01-01 --facebook-end-date 2019-01-01 write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_facebook``

---------------
Command options
---------------

==================================  ==============================================================================================================================================================================================================================
Options                             Definition
==================================  ==============================================================================================================================================================================================================================
``--facebook-app-id``               Facebook App ID. Not mandatory if Facebook Access Token is provided.
``--facebook-app-secret``           Facebook App Secret. Not mandatory if Facebook Access Token is provided.
``--facebook-access-token``         Facebook App Access Token.
``--facebook-object-type``          Nature of the root Facebook Object used to make the request. Possible values: pixel (Ad Management requests only), creative (Ad Management requests only), ad, adset, campaign, account (default).
``--facebook-object-id``            ID of the root Facebook Object used to make the request.
``--facebook-level``                Granularity of the response. Possible values: pixel (Ad Management requests only), creative (Ad Management requests only), ad (default), adset, campaign, account.
``--facebook-ad-insights``          True (default) if Ad Insights request, False if Ad Management request.
``--facebook-field``                Fields to be retrieved.
``--facebook-start-date``           Start date of the period to request (format: YYYY-MM-DD). This parameter is only relevant for Ad Insights Requests, and Ad Management requests at the Campaign, Adset and Ad levels.
``--facebook-end-date``             Start date of the period to request (format: YYYY-MM-DD). This parameter is only relevant for Ad Insights Requests, and Ad Management requests at the Campaign, Adset and Ad levels.
``--facebook-date-preset``          Relative time range. Ignored if ``--facebook-start-date`` and ``--facebook-end-date`` are specified. This parameter is only relevant for Ad Insights Requests, and Ad Management requests at the Campaign, Adset and Ad levels.
``--facebook-time-increment``       Cuts the results between smaller time slices within the specified time range. This parameter is only relevant for Ad Insights Requests, and Ad Management requests at the Campaign, Adset and Ad levels.
``--facebook-add-date-to-report``   True if you wish to add the date of the request to each response record, False otherwise (default).
``--facebook-breakdown``            How to break down the result. This parameter is only relevant for Ad Insights Requests.
``--facebook-action-breakdown``     How to break down action results. This parameter is only relevant for Ad Insights Requests.
==================================  ==============================================================================================================================================================================================================================

1. Make sure to select the appropriate ``--facebook-level``

================================== =============================================
If Facebook Object Type is...      Facebook Level can be...
================================== =============================================
``account``                        account, campaign, adset, ad, creative, pixel
``campaign``                       campaign, adset, ad
``adset``                          adset, ad, creative
``ad``                             ad, creative
``creative``                       creative
``pixel``                          pixel
================================== =============================================

2. Format Facebook Marketing Reader response using ``--facebook-fields``

2.1. The list of applicable fields can be found on the links below:

- Ad Insights Request: `all fields <https://developers.facebook.com/docs/marketing-api/insights/parameters/v7.0>`__
- Ad Management Request: `Account-level fields <https://developers.facebook.com/docs/marketing-api/reference/ad-account>`__, `Campaign-level fields <https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group>`__, `Adset-level fields <https://developers.facebook.com/docs/marketing-api/reference/ad-campaign>`__, `Ad-level fields <https://developers.facebook.com/docs/marketing-api/reference/adgroup>`__, `Creative-level fields <https://developers.facebook.com/docs/marketing-api/reference/ad-creative>`__, `Pixel-level fields <https://developers.facebook.com/docs/marketing-api/reference/ads-pixel/>`__

2.2. If you want to select a nested field value, simply indicate the path to this value within the request field.

*Facebook Marketing Reader Request*

.. code-block:: shell

    --facebook-field object_story_spec[video_data][call_to_action][value][link]

*API Response*

.. code-block:: shell

    "object_story_spec": {
        "video_data": {
            "call_to_action": {
                "type": "LEARN_MORE",
                "value": {
                    "link": "https://www.artefact.com",
                    "link_format": "VIDEO_LPP"
                }
            }
        }
    }

*Facebook Marketing Reader Response*

.. code-block:: shell

    {"object_story_spec_video_data_call_to_action_value_link": "https://www.artefact.com"}

2.3 Action Breakdown filters can be applied to the fields of Ad Insights Requests using the following syntax: <FIELD_NAME>[<ACTION_BREAKDOWN>:<ACTION_BREAKDOWN_VALUE>]. You can combine multiple Action Breakdown filters on the same field by adding them in cascade next to each other.

*Facebook Marketing Reader Request*

.. code-block:: shell

    --facebook-action-breakdown action_type
    --facebook-field actions[action_type:video_view][action_type:post_engagement]

*API Response*

.. code-block:: shell

    "actions": [
        {
            "action_type": "video_view",
            "value": "17"
        },
        {
            "action_type": "link_click",
            "value": "8"
        },
        {
            "action_type": "post_engagement",
            "value": "25"
        },
        {
            "action_type": "page_engagement",
            "value": "12"
        }
    ]

*Facebook Marketing Reader Response*

.. code-block:: shell
    
    {"actions_action_type_video_view": "17", "actions_action_type_post_engagement": "25"}

==============
Google Readers
==============

--------------
Authentication
--------------

You can authenticate to most of the Readers of the Google Suite following the same schema. You'll need to generate a **refresh token** to connect via the OAuth flow. A full script to do this can be found in this `refresh token generator <https://github.com/artefactory/Refresh-token-generator-for-google-oauth>`__.

=================
Google Ads Reader
=================

----------
Source API
----------

`AdWords API <https://developers.google.com/adwords/api/docs/guides/start>`__

-------------------------
How to obtain credentials
-------------------------

Using the AdWords API requires four things:

- A developer token (Generated at a company level - one per company -, takes around 2 days to be approved by Google) which can be completely independant from the Google Ads Account you will be calling (though you need a Manager Google Ads Account to request a token for your company)
- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>
- A refresh token, created with the email address able to access to all the Google Ads Account you will be calling
- The ID of the Google Ads Accounts <CLIENT_CUSTOMER_ID> you will be reading from (XXX-XXX-XXXX numbers, written right next to your Account Name)

See the `documentation here <https://developers.google.com/adwords/api/docs/guides/signup>`__ to apply for access if your Company does not already have a developer token (granting you the right to use the API).

See the `documentation here <https://developers.google.com/adwords/api/docs/guides/first-api-call>`__ to set-up your OAuth2 credentials and refresh token specifically for your Google Ads Accounts.

----------
Quickstart
----------

The following command retrieves insights about the Ads of ``my_first_campaign``and ``my_second_campaign`` in the Google Ads Account <CLIENT_CUSTOMER_ID>.

.. code-block:: shell

    python nck/entrypoint.py read_googleads --googleads-developer-token <DEVELOPER_TOKEN> --googleads-client-id <CLIENT_ID> --googleads-client-secret <CLIENT_SECRET> --googleads-refresh-token <REFRESH_TOKEN> --googleads-client-customer-id <XXX-XXX-XXXX CLIENT_CUSTOMER_ID> --googleads-report-type AD_PERFORMANCE_REPORT --googleads-date-range-type LAST_7_DAYS --googleads-field CampaignName --googleads-field AdGroupName --googleads-field Headline --googleads-field Date --googleads-field Impressions --googleads-report-filter "{'field':'CampaignName','operator':'IN','values':['my_first_campaign','my_second_campaign']}"

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_googleads``

---------------
Command options
---------------

==========================================  ==========================================================================================================================================================================================================
Options                                     Definition
==========================================  ==========================================================================================================================================================================================================
``--googleads-developer-token``             Company Developer token for Google Ads API
``--googleads-client-id``                   OAuth2 ID
``--googleads-client-secret``               OAuth2 secret
``--googleads-refresh-token``               Refresh token for OAuth2
``--googleads-manager-id``                  (Optional) Manager_Account_ID (XXX-XXX-XXXX identifier)
``--googleads-client-customer-id``          GAds_Account_ID (ignored if a manager account ID was given)
``--googleads-report-name``                 (Optional) Name of your output stream ("Custom Report" by default)
``--googleads-report-type``                 Type of report to be called
``--googleads-date-range-type``             Type of date range to apply (if "CUSTOM_RANGE", a min and max date must be specified). Possible values can be found `here <https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges>`__.
``--googleads-start-date``                  (Optional) Start date for "CUSTOM_RANGE" date range (format: YYYY-MM-DD)
``--googleads-end-date``                    (Optional) End date for "CUSTOM_RANGE" date range (format: YYYY-MM-DD)
``--googleads-field``                       Fields to include in the report
``--googleads-report-filter``               Filter to apply on a chosen field (Dictionary as String "{'field':,'operator':,'values':}")
``--googleads-include-zero-impressions``    Boolean specifying whether or not rows with zero impressions should be included in the report
``--googleads-filter-on-video-campaigns``   Boolean used to filter the report on Video Campaigns only (require CampaignId to be listed as a field)
``--googleads-include-client-customer-id``  Boolean used to add "AccountId" as a field in the output stream. AccountId is not available in the API, but is known since it's a requirement to call the API (= Client Customer ID)
==========================================  ==========================================================================================================================================================================================================

See documentation below for a better understanding of the parameters:

- `Reporting basics <https://developers.google.com/adwords/api/docs/guides/reporting#create_a_report_definition>`__
- `Available reports and associated fields <https://developers.google.com/adwords/api/docs/appendix/reports#available-reports>`__

=======================
Google Analytics Reader
=======================

----------
Source API
----------

`Analytics Reporting API <https://developers.google.com/analytics/devguides/reporting/core/v4>`__

----------
Quickstart
----------

The following command retrieves sessions, pageviews and bounces volumes by date from 2020-01-01 to 2020-01-03, for the Analytics View <VIEW_ID>.

.. code-block:: shell

    python nck/entrypoint.py read_ga --ga-client-id <CLIENT_ID> --ga-client-secret <CLIENT_SECRET> --ga-view-id <VIEW_ID> --ga-refresh-token <REFRESH_TOKEN> --ga-dimension ga:date --ga-metric sessions --ga-metric ga:pageviews --ga-metric ga:bounces --ga-start-date 2020-01-01 --ga-end-date 2020-01-03 write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_ga``

---------------
Command options
---------------

==============================  ===============================================================================================================================================================================================================
Options                         Definition
==============================  ===============================================================================================================================================================================================================
``--ga-client-id``              OAuth2 ID
``--ga-client-secret``          OAuth2 secret
``--ga-access-token``           (Optional) Access token for OAuth2
``--ga-refresh-token``          Refresh token for OAuth2
``--ga-view-id``                Analytics View ID from which to retrieve data. See documentation `here <https://support.google.com/analytics/answer/1009618>`__ for a better understanding of Google Analytics hierrarchy.
``--ga-account-id``             Analytics Account ID from which to retrieve data. See documentation `here <https://support.google.com/analytics/answer/1009618>`__ for a better understanding of Google Analytics hierrarchy.
``--ga-dimension``              Dimensions to include in the report (max 9). Possible values can be found `here <https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/>`__.
``--ga-metric``                 Metrics to include in the report (min 1, max 10). Possible values can be found `here <https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/>`__.
``--ga-segment-id``             Segment ID of a built-in or custom segment (for example gaid::-3) on which report data should be segmented.
``--ga-start-date``             Start date of the period to request (format: YYYY-MM-DD)
``--ga-end-date``               End date of the period to request (format: YYYY-MM-DD)
``--ga-date-range``             <START_DATE> <END_DATE> of the period to request, specified as a unique argument (format: YYYY-MM-DD YYYY-MM-DD)
``--ga-day-range``              Relative time range. Possible values: PREVIOUS_DAY, LAST_30_DAYS, LAST_7_DAYS, LAST_90_DAYS.
``--ga-sampling-level``         Desired sample size. See documentation `here <https://support.google.com/analytics/answer/2637192>`__ for a better understanding of Google Analytics sampling. Possible values: SMALL, DEFAULT, LARGE (default).
``--ga-add-view``               If set to True (default: False), adds a "ga:viewId" field to the output stream.
==============================  ===============================================================================================================================================================================================================

See documentation `here <https://developers.google.com/analytics/devguides/reporting/core/v4/basics>`__ for a better understanding of the parameters.

===========================
Google Cloud Storage Reader
===========================

----------
Source API
----------

`GCP Client Library for Cloud Storage <https://googleapis.dev/python/storage/latest/client.html>`__

----------
Quickstart
----------

Follow these steps to set your credentials:

- In your GCP project, create a Service Account with a 'Storage Object Viewer' role
- Create a .json key for this Service Account, and download the key file locally
- Execute the following commands:

.. code-block:: shell

    export project_id=<GCP project ID>
    export GCP_KEY_PATH=<Path to the Service Account key file>

Once done, launch your Google Cloud Storage reader command. The following command retrieves the blobs located under the Google Cloud Storage bucket ``daily_reports`` and the blob prefix ``FR/offline_sales/``:

.. code-block:: shell

    python nck/entrypoint.py read_gcs --gcs-bucket daily_reports --gcs-prefix FR/offline_sales --gcs-format csv write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_gcs``

---------------
Command options
---------------

==============================  ========================================================================================================================================================================================================================================================================================================================================================================================================================
Options                         Definition
==============================  ========================================================================================================================================================================================================================================================================================================================================================================================================================
``--gcs-bucket``                Cloud Storage bucket name
``--gcs-prefix``                Cloud Storage blob prefix. Several prefixes can be provided in a single command.
``--gcs-format``                Cloud Storage blob format. *Possible values: csv, gz*
``--gcs-dest-key-split``        Indicates how to retrieve a blob name from a blob key (a blob key being the combination of a blob prefix and a blob name: <BLOB_PREFIX>/<BLOB_NAME>). The reader splits the blob key on the "/" character: the last element of the output list is considered as the blob name, and is used to name the stream produced by the reader. This option defines how many splits to do. *Default: -1 (split on all occurences)*
``--gcs-csv-delimiter``         Delimiter that should be used to read the .csv file. *Default: ,*
``--gcs-csv-fieldnames``        List of field names. If set to *None* (*default*), the values in the first row of .csv file will be used as field names.
==============================  ========================================================================================================================================================================================================================================================================================================================================================================================================================

==============================
Google Campaign Manager Reader
==============================

----------
Source API
----------

`DCM/DFA Reporting and Trafficking API <https://developers.google.com/doubleclick-advertisers/v3.3>`__

----------
Quickstart
----------

The following command retrieves impressions, clicks and cost volumes from 2020-01-01 to 2020-01-03.

.. code-block:: shell
    
    python nck/entrypoint.py read_dcm --dcm-client-id <CLIENT_ID> --dcm-client-secret <CLIENT_SECRET> --dcm-refresh-token <REFRESH_TOKEN> --dcm-profile-id <PROFILE_ID> --dcm-dimension dfa:date --dcm-metric dfa:impressions --dcm-metric dfa:clicks --dcm-metric dfa:mediaCost --dcm-start-date 2020-01-01 --dcm-end-date 2020-01-03 write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_dcm``

---------------
Command options
---------------

==============================  =======================================================================================================================================================================================================================================================================================================================================
Options                         Definition
==============================  =======================================================================================================================================================================================================================================================================================================================================
``--dcm-client-id``             OAuth2 ID
``--dcm-client-secret``         OAuth2 secret
``--dcm-access-token``          (Optional) Access token for OAuth2
``--dcm-refresh-token``         Refresh token for OAuth2
``--dcm-profile-id``            ID of the DFA user profile that has been granted permissions to the CM account for which you want to retrieve data. You should have 1 DFA user profile per CM account that you can access. The associated ID can be found directly on your Campaign Manager UI (when accessing your list of CM accounts, on the top right hand corner).
``--dcm-report-name``           Name of the report, that will appear in CM UI.
``--dcm-report-type``           Type of the report. Possible values: CROSS_DIMENSION_REACH, FLOODLIGHT, PATH_TO_CONVERSION, REACH, STANDARD.
``--dcm-dimension``             Dimensions to include in the report. Possible values can be found `here <https://developers.google.com/doubleclick-advertisers/v3.3/dimensions>`__.
``--dcm-metric``                Metrics to include in the report. Possible values can be found `here <https://developers.google.com/doubleclick-advertisers/v3.3/dimensions>`__.
``--dcm-filter``                <FILTER_TYPE> <FILTER_VALUE> association, used to narrow the scope of the report. For instance "dfa:advertiserId XXXXX" will narrow report scope to the performance of Advertiser ID XXXXX. Possible filter types can be found `here <https://developers.google.com/doubleclick-advertisers/v3.3/dimensions>`__.
``--dcm-start-date``            Start date of the period to request (format: YYYY-MM-DD)
``--dcm-end-date``              End date of the period to request (format: YYYY-MM-DD)
==============================  =======================================================================================================================================================================================================================================================================================================================================

===========================================
Google DoubleClick Bid Manager Reader (DBM)
===========================================

----------
Source API
----------

`Doubleclick Bid Manager API <https://developers.google.com/bid-manager/v1>`__

----------
Quickstart
----------

The following command retrieves impressions, clicks and cost volumes filtered on a specific <ADVERTISER_ID> from 2020-01-01 to 2020-01-03.

.. code-block:: shell

    python nck/entrypoint.py read_dbm --dbm-client-id <CLIENT_ID> --dbm-client-secret <CLIENT_SECRET> —dbm-refresh-token <REFRESH_TOKEN> —dbm-filter FILTER_ADVERTISER <ADVERTISER_ID> --dbm-query-dimension FILTER_DATE  --dbm-query-metric METRIC_IMPRESSIONS --dbm-query-metric METRIC_CLICKS --dbm-query-metric METRIC_MEDIA_COST_ADVERTISER --dbm-query-param-type TYPE_GENERAL --dbm-request-type custom_query_report --dbm-start-date 2020-01-01 --dbm-end-date 2020-01-03 write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_dbm``

---------------
Command options
---------------

==============================  ================================================================================================================================================================================================================================================================================================================
Options                         Definition
==============================  ================================================================================================================================================================================================================================================================================================================
``--dbm-client-id``             OAuth2 ID
``--dbm-client-secret``         OAuth2 secret
``--dbm-access-token``          (Optional) Access token for OAuth2
``--dbm-refresh-token``         Refresh token for OAuth2
``--dbm-query-request-type``    Doubleclick Bid Manager API request type. Possible values: existing_query, custom_query, existing_query_report, custom_query_report, lineitems_objects, sdf_objects and list_reports.
``--dbm-query-id``              Query ID.
``--dbm-query-title``           Query title, used to name the reports generated from this query in DV360 UI.
``--dbm-query-frequency``       How often the query is run. Possible values can be found `here <https://developers.google.com/bid-manager/v1/queries#schedule.frequency>`__. Default: ONE_TIME.
``--dbm-filter``                <FILTER_TYPE> <FILTER_VALUE> association, used to narrow the scope of the report. For instance "FILTER_ADVERTISER XXXXX" will narrow report scope to the performance of Advertiser ID XXXXX. Possible filter types can be found `here <https://developers.google.com/bid-manager/v1/filters-metrics#filters)>`__.
``--dbm-query-dimension``       Dimensions to include in the report. Possible values can be found `here <https://developers.google.com/bid-manager/v1/filters-metrics#filters>`__.
``--dbm-query-metric``          Metrics to include in the report. Possible values can be found `here <https://developers.google.com/bid-manager/v1/filters-metrics#metrics>`__.
``--dbm-query-param-type``      Report type. Possible values can be found `here <https://developers.google.com/bid-manager/v1/queries#params.type>`__. Default: TYPE_TRUEVIEW.
``--dbm-start-date``            Start date of the period to request (format: YYYY-MM-DD)
``--dbm-end-date``              End date of the period to request (format: YYYY-MM-DD)
==============================  ================================================================================================================================================================================================================================================================================================================

===================
Google DV360 Reader
===================

----------
Source API
----------

`DV360 API <https://developers.google.com/display-video/api/guides/getting-started/overview>`__

-------------------------
How to obtain credentials
-------------------------

As for DBM, the DV360 API uses OAuth 2.0 for authentication. There is not a single way to generate credentials but one is descrived below:

- Enable DV360 API in a GCP project
- Generate a client id / client secret pair
- Log in with the user that can access DV360
- Go to the `OAuth 2.0 Playground <https://developers.google.com/oauthplayground/>`__

  - Go to the OAuth 2.0 configuration (the wheel in the upper right corner) and put your client id and client secret
  - Select the DV360 API
  - Exchange authorization codes for tokens. This is where you may have to log in with the account that can access DV360

You should now have an access token and a refresh token. Save them carefully. 

----------
Quickstart
----------

Say you want to get a SDF file for all campaigns of a specific advertiser. You can run:

.. code-block:: shell
    
    python nck/entrypoint.py read_dv360 --dv360-client-id <CLIENT_ID> --dv360-client-secret <CLIENT_SECRET> --dv360-refresh-token <REFRESH_TOKEN> --dv360-access-token <ACCESS_TOKEN> --dv360-advertiser-id <ADVERTISER_ID> --dv360-filter-type 'FILTER_TYPE_NONE' --dv360-file-type 'FILE_TYPE_CAMPAIGN' write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_dv360``

---------------
Command options
---------------

==============================  ===============================================================
Options                         Definition
==============================  ===============================================================
``--dv360-access-token``        Access token you during the process of getting tokens
``--dv360-refresh-token``       Refresh token you during the process of getting tokens
``--dv360-client-id``           Client ID you generated in the GCP environment
``--dv360-client-secret``       Client secret you generated in the GCP environment
``--dv360-advertiser-id``       One of the advertiser IDs you have access to
``--dv360-request-type``        Request type. Choose among 'sdf_request' and 'creative_request'
``--dv360-file-type``           SDF level
``--dv360-filter-type``         SDF filter. Depends on the level.
==============================  ===============================================================

============================
Google Search Console Reader
============================

----------
Source API
----------

`Search Console API (Search Analytics endpoint) <https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/>`__

-------------------------
How to obtain credentials
-------------------------

Using the Google Search Console API requires three main parameters:

- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>
- A refresh token, created with the email address able to access to your Google Search Console Account.
- The URLs whose performance you want to see

----------
Quickstart
----------

The following command retrieves insights about the URL <SITE_URL> from 2020-01-01 to 2020-01-03.

.. code-block:: shell

    python nck/entrypoint.py read_search_console --search-console-client-id <CLIENT_ID> --search-console-refresh-token <REFRESH_TOKEN> --search-console-site-url <SITE_URL> --search-console-dimensions country --search-console-dimensions device --search-console-start-date 2020-01-01 --search-console-end-date 2020-01-03 write_console 

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_search_console``

---------------
Command options
---------------

==================================  ============================================================================================================================================================================================================
Options                             Definition
==================================  ============================================================================================================================================================================================================
``--search-console-client-id``      OAuth2 ID
``--search-console-client-secret``  OAuth2 secret
``--search-console-access-token``   Access token for OAuth2
``--search-console-refresh-token``  Refresh token for OAuth2
``--search-console-dimensions``     Dimensions of the report. Possible values can be found `here <https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query#dimensionFilterGroups.filters.dimension>`__.
``--search-console-site-url``       Site URL whose performance you want to request
``--search-console-start-date``     Start date of the period to request (format: YYYY-MM-DD)
``--search-console-end-date``       End date of the period to request (format: YYYY-MM-DD)
``--search-console-date-column``    If set to True, a date column will be included in the report
``--search-console-row-limit``      Row number by report page
==================================  ============================================================================================================================================================================================================

See documentation `here <https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query>`__ for a better understanding of the parameters.

============================
Google Search Ads 360 Reader
============================

----------
Source API
----------

`Search Ads 360 API <https://developers.google.com/search-ads/v2/reference>`__

-------------------------
How to obtain credentials
-------------------------

Using the Search Ads API requires two things:
- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>
- A refresh token, created with the email address able to access to all the Search Ads 360 Account you will be calling

See the `documentation here <https://developers.google.com/search-ads/v2/authorizing "SA360 Authentication">`__
to set-up your OAuth2 credentials and refresh token specifically for Search Ads 360 Reporting.

----------
Quickstart
----------

The following command retrieves insights about the Ads in the Search Ads 360 Account <ADVERTISER_ID> from the agency <AGENCY_ID>.

.. code-block:: shell

    python nck/entrypoint.py read_sa360 --sa360-client-id <CLIENT_ID> --sa360-client-secret <CLIENT_SECRET> --sa360-refresh-token <REFRESH_TOKEN> --sa360-agency-id <AGENCY_ID> --sa360-advertiser-id <ADVERTISER_ID> --sa360-report-type keyword --sa360-column date --sa360-column impr --sa360-column clicks --sa360-start-date 2020-01-01 --sa360-end-date 2020-01-01 

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_sa360``

---------------
Command options
---------------

==============================  =====================================================================================================================================================
Options                         Definition
==============================  =====================================================================================================================================================
``--sa360-client-id``           OAuth2 ID
``--sa360-client-secret``       OAuth2 secret
``--sa360-access-token``        (Optional) Access token
``--sa360-refresh-token``       Refresh token
``--sa360-agency-id``           Agency ID to request in SA360
``--sa360-advertiser-id``       (Optional) Advertiser ids to request. If not provided, every advertiser of the agency will be requested
``--sa360-report-name``         (Optional) Name of the output report
``--sa360-report-type``         Type of the report to request. Possible values can be found `here <https://developers.google.com/search-ads/v2/report-types>`__.
``--sa360-column``              Dimensions and metrics to include in the report
``--sa360-saved-column``        (Optional) Saved columns to report. Documentation can be found `here <https://developers.google.com/search-ads/v2/how-tos/reporting/saved-columns>`__.
``--sa360-start-date``          Start date of the period to request (format: YYYY-MM-DD)
``--sa360-end-date``            End date of the period to request (format: YYYY-MM-DD)
==============================  =====================================================================================================================================================

See documentation `here <https://developers.google.com/search-ads/v2/how-tos/reporting>`__ for a better understanding of the parameters.

====================
Google Sheets Reader
====================

----------
Source API
----------

`Google Sheets API <https://developers.google.com/sheets/api>`__

-------------------------
How to obtain credentials
-------------------------

To use the Google Sheets Reader you must first retrieve your credentials. In order to do so, head to console.cloud.google.com. In the header, chose your project or create a new one. Next step is to enable the Google Drive and Google Sheets APIs in the API Library. You’ll find it in the *APIs & Services* tab. Now that Google Drive API is enabled, click on the *Create credentials* button on the upper-right corner and enter these informations :

- Which API are you using? > Google Drive API
- Where will you be calling the API from? > Web server
- What data will you be accessing? > Application data
- Are you planning to use this API with App Engine or Compute Engine? > No, I'm not using them

Click on *What credentials do I need* and complete the form. You will find the credentials you need in the .json file that will start downloading automatically right after.

----------
Quickstart
----------

This command allows you to retrieve the desired information from a Google Sheet file row-by-row in a dictionary format. For example, given 3 columns a, b, c and 2 rows with respectively the values d, e, f and g, h, i, we would obtain such a dictionary:

.. code-block:: shell

    {"a": "d", "b": "e", "c": "f"}
    {"a": "g", "b": "h", "c": "i"}

------------
Command name
------------

``read_gs``

---------------
Command options
---------------

==============================  ==============================================================================================================================================================
Options                         Definition
==============================  ==============================================================================================================================================================
``--gs-project-id``             Project ID that is given by Google services once you have created your project in the Google Cloud Console. You can retrieve it in the .json credential file.
``--gs-private-key-id``         Private key ID given by Google services once you have added credentials to the project. You can retrieve it in the .json credential file.
``--gs-private-key-path``       The path to the private key that is stored in a txt file. You can retrieve it first in the .json credential file.
``--gs-client-email``           Client e-mail given by Google services once you have added credentials to the project. You can retrieve it in the .json credential file.
``--gs-client-id``              Client ID given by Google services once you have added credentials to the project. You can retrieve it in the .json credential file.
``--gs-client-cert``            Client certificate given by Google services once you have added credentials to the project. You can retrieve it in the .json credential file.
``--gs-file-name``              The name you have given to your Google Sheet file
``--gs-page-number``            The page number you want to access. The number pages starts at 0.
==============================  ==============================================================================================================================================================

===================
MyTarget Reader
===================

----------
Source API
----------

`Mytarget API <https://target.my.com/help/advertisers/api_arrangement/en>`__

-------------------------
How to obtain credentials
-------------------------

The mytarget API uses the OAuth2 protocol. There is not a single way to generate credentials, you can find the 3 ways to retrieve your credentials below :

`Get your mytarget credentials <https://target.my.com/help/advertisers/api_authorization/en>`__

You should now have an access token and a refresh token. Save them carefully. 

----------
Quickstart
----------

Say you want to retrieve for all campaigns and its associated banners and stats of a specific advertiser from the 01/01/2020 to the 07/01/2020. You can run:

.. code-block:: shell
    
    python nck/entrypoint.py read_mytarget --mytarget-client-id <CLIENT_ID> --mytarget-client-secret <CLIENT_SECRET> --mytarget-refresh-token <REFRESH_TOKEN> --mytarget-request-type 'general' --mytarget-start-date <START_DATE> --mytarget-end-date <END_DATE> write_console


If you just want to get the budget instead of the general statistics of each campaign you can try the following:

.. code-block:: shell
    
    python nck/entrypoint.py read_mytarget --mytarget-client-id <CLIENT_ID> --mytarget-client-secret <CLIENT_SECRET> --mytarget-refresh-token <REFRESH_TOKEN> --mytarget-request-type 'budget' --mytarget-start-date <START_DATE> --mytarget-end-date <END_DATE> write_console


*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_mytarget``

---------------
Command options
---------------

==============================  ===============================================================
Options                         Definition
==============================  ===============================================================
``--mytarget-client-id``        Client ID you generated
``--mytarget-client-secret``    Client secret you generated. 
``--mytarget-refresh-token``    Secret token you retrieved during the process of getting tokens
``--mytarget-request-type``     Type of report you want to retrieve: performance or budgets.
``--mytarget-start-date``       Start date of the period to request (format: YYYY-MM-DD)
``--mytarget-end-date``         End date of the period to request (format: YYYY-MM-DD)
==============================  ===============================================================

============
MySQL Reader
============

----------
Source ORM
----------

`SQL Alchemy <https://docs.sqlalchemy.org/en/13/>`__ (using the ``mysql+pymysql`` engine)

----------
Quickstart
----------

The following command retrieves all records from the table <TABLE_NAME> (equivalent to ``SELECT * FROM <TABLE_NAME>``).

.. code-block:: shell

    python nck/entrypoint.py read_mysql --mysql-user <DATABASE_USER> --mysql-password <DATABASE_PASSWORD> --mysql-host <DATABASE_HOST> --mysql-port <DATABASE_PORT> --mysql-database <DATABASE_NAME> --mysql-table <TABLE_NAME> write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_mysql``

---------------
Command options
---------------

=====================================  =========================================================================================================
Options                                Definition
=====================================  =========================================================================================================
``--mysql-user``                       Database user
``--mysql-password``                   Database password
``--mysql-host``                       Database host
``--mysql-port``                       Database port
``--mysql-database``                   Database name
``--mysql-query``                      SQL query (you must specify either a query or a table)
``--mysql-query-name``                 SQL query name (required if you specify a query)
``--mysql-table``                      Database table on which you want to run a `SELECT *` query (you must specify either a query or a table)
``--mysql-watermark-column``           Watermark column (required when using state management)
``--mysql-watermark-init``             Initial watermark column value (required when using state management)
``--mysql-redis-state-service-name``   Redis state service hash name
``--mysql-redis-state-service-host``   Redis state service host
``--mysql-redis-state-service-port``   Redis state service port
=====================================  =========================================================================================================

==============
Radarly Reader
==============

----------
Source API
----------

`Radarly API <https://github.com/linkfluence/radarly-py>`__

----------
Quickstart
----------

The following command retrieves data from posts located under the project ``<PROJECT_ID>`` and associated to the focus IDs ``00001`` and ``00002``, from 2020-01-01 to 2020-01-03.

.. code-block:: shell

    python nck/entrypoint.py read_radarly --radarly-client-id <CLIENT_ID> --radarly-client-secret <CLIENT_SECRET> --radarly-pid <PROJECT_ID> --radarly-focus-id 00001 --radarly-focus-id 00002 --radarly-start-date 2020-01-01 --radarly-end-date 2020-01-03

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_radarly``

---------------
Command options
---------------

==============================================  ======================================================================================================================================================================================================================
Options                                         Definition
==============================================  ======================================================================================================================================================================================================================
``--radarly-client-id``                         Radarly Client ID
``--radarly-client-secret``                     Radarly Client Secret
``--radarly-pid``                               Radarly Project ID
``--radarly-focus-id``                          Focus IDs (several can be provided)
``--radarly-start-date``                        Start date of the period to request
``--radarly-end-date``                          End date of the period to request
``--radarly-api-request-limit``                 Max number of posts to be requested in a single API request
``--radarly-api-date-period-limit``             Max number of posts to be requested in a single Search query
``--radarly-api-window``                        Duration of the rate limit window
``--radarly-api-quaterly-posts-limit``          Max number of posts to be requested over the rate limit window
``--radarly-api-throttle``                      If set to True (default), forces the reader to abide by `official API rate limits <https://github.com/linkfluence/radarly-py/blob/master/docs/officialdoc/introduction/rates.rst>`__, using the 2 above parameters.
``--radarly-throttling-threshold-coefficient``  Throttling threshold coefficient
==============================================  ======================================================================================================================================================================================================================

=================
Salesforce Reader
=================

----------
Source API
----------

`Lightning Platform REST API <https://developer.salesforce.com/docs/atlas.en-us.212.0.api_rest.meta/api_rest/intro_what_is_rest_api.html>`__

----------
Quickstart
----------

The following command retrieves name field values from all Account records.

.. code-block:: shell

    python nck/entrypoint.py read_salesforce --salesforce-consumer-key <CONSUMER_KEY> --salesforce-consumer-secret <CONSUMER_SECRET> --salesforce-user <USERNAME> --salesforce-password <PASSWORD> --salesforce-query 'SELECT name FROM Account' --salesforce-query-name nck-account-name-query write_console

*Didn't work?* See the `Troubleshooting`_ section.

-------------------------
How to obtain credentials
-------------------------

Create a Connected App by following the instructions detailed `on this page <https://developer.salesforce.com/docs/atlas.en-us.212.0.api_rest.meta/api_rest/quickstart_oauth.html>`__: it will generate your authentication credentials.

------------
Command name
------------

``read_salesforce``

---------------
Command options
---------------

==================================  =================================================================================================================================================================================================================================================================================================
Options                             Definition
==================================  =================================================================================================================================================================================================================================================================================================
``--salesforce-consumer-key``       Client ID of your Salesforce Connected App
``--salesforce-consumer-secret``    Client Secret of your Salesforce Connected App
``--salesforce-user``               Salesforce username
``--salesforce-password``           Salesforce password
``--salesforce-object-type``        Salesforce object type (you must specify either a Salesforce object type or a SOQL query). With this configuration, the command will retrieve the values of all the fields from the given object records (equivalent to the SOQL query: `SELECT <LIST OF ALL OBJECT FIELDS> FROM <OBJECT TYPE>`).
``--salesforce-query``              SOQL query (you must specify either a Salesforce object type or a SOQL query). You can find documentation on Salesforce Object Query Language (SOQL) `here <https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.html>`__.
``--salesforce-query-name``         SOQL query name (required if you specify a SOQL query)
``--salesforce-watermark-column``   Salesforce watermark column (required when using state management)
``--salesforce-watermark-init``     Initial Salesforce watermark column value (required when using state management)
==================================  =================================================================================================================================================================================================================================================================================================

=====================
The Trade Desk Reader
=====================

----------
Source API
----------

`The Trade Desk API <https://api.thetradedesk.com/v3/portal/api/doc/ApiOverview>`__

-------------------------
How to obtain credentials
-------------------------

- Ask your Account Representative to **give you access to The Trade Desk API and UI**
- He will generally provide you with **two distinct accounts**:  an **API account**, allowing you to make API calls (*Login: ttd_api_{XXXXX}@client.com*), and a **UI account**, allowing you to navigate on The Trade Desk UI to create Report Templates (*Login: your professional e-mail address*)
- Pass **the Login and Password of your API account** to The Trade Desk connector

----------
Quickstart
----------

To request dimensions and metrics to The Trade Desk API, you should first **create a Report Template in The Trade Desk UI**, by following the below process:

- Connect to `The Trade Desk UI <https://desk.thetradedesk.com/>`__ using the Login and Password of your UI account
- Navigate to *Reports* > *My Reports* to land on the *Report Templates* section
- Clone an existing Report Template, edit it to keep only the dimensions and metrics that you want to collect, and save it: it will appear under the *Mine* section
- Provide the exact name of the Report Template you have just created under the CLI option ``--ttd-report-template-name`` of The Trade Desk connector: the connector will "schedule" a report instance (which may take a few minutes to run), and fetch data to the location of your choice

The following command retrieves the data associated to the Report template named "*adgroup_performance_report*" between 2020-01-01 and 2020-01-03, filtered on the PartnerId <PARTNER_ID>.

.. code-block:: shell

    python nck/entrypoint.py read_ttd --ttd-login <LOGIN> --ttd-password <PASSWORD> --ttd-partner-id <PARTNER_ID> --ttd-report-template-name adgroup_performance_report --ttd-start-date 2020-01-01  --ttd-end-date 2020-01-03 write_console

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Command the name

``read_ttd``

---------------
Command options
---------------

==============================  ===========================================================================================================================================================================================
Options                         Definition
==============================  ===========================================================================================================================================================================================
``--ttd-login``                 Login of your API account
``--ttd-password``              Password of your API account
``--ttd-advertiser-id``         Advertiser Ids for which report data should be fetched
``--ttd-report-template-name``  Exact name of the Report Template to request. Existing Report Templates can be found within the `MyReports section <https://desk.thetradedesk.com/MyReports>`__ of The Trade Desk UI.
``--ttd-report-schedule-name``  Name of the Report Schedule to create
``--ttd-start-date``            Start date of the period to request (format: YYYY-MM-DD)
``--ttd-end-date``              End date of the period to request (format: YYYY-MM-DD)
``--ttd-normalize-stream``      If set to True, yields a NormalizedJSONStream (spaces and special characters replaced by '_' in field names, which is useful for BigQuery). Else (default), yields a standard JSONStream.
==============================  ===========================================================================================================================================================================================

If you need any further information, the documentation of The Trade Desk API can be found `here <https://api.thetradedesk.com/v3/portal/api/doc/ApiOverview>`__.

==================
Twitter Ads Reader
==================

----------
Source API
----------

`Twitter Ads API <https://developer.twitter.com/en/docs/ads/general/overview>`__

-------------------------
How to obtain credentials
-------------------------

- **Apply for a developer account** through `this link <https://developer.twitter.com/en/apply>`__.
- **Create a Twitter app** on the developer portal: it will generate your authentication credentials.
- **Apply for Twitter Ads API access** by filling out `this form <https://developer.twitter.com/en/docs/ads/general/overview/adsapi-application>`__. Receiving Twitter approval may take up to 7 business days.
- **Get access to the Twitter Ads account** you wish to retrieve data for, on the @handle that you used to create your Twitter App. Be careful, access levels matter: with an *Ad Manager* access, you will be able to request all report types; with a *Campaign Analyst* access, you will be able to request all report types, except ENTITY reports on Card entities.

----------
Quickstart
----------

The Twitter Ads Reader can collect **3 types of reports**, making calls to 4 endpoints of the Twitter Ads API:

- **ANALYTICS reports**, making calls to the `Asynchronous Analytics endpoint <https://developer.twitter.com/en/docs/ads/analytics/api-reference/asynchronous>`__. These reports return performance data for a wide range of metrics, that **can be aggregated over time**. Output data **can be splitted by day** when requested over a larger time period.
- **REACH reports**, making calls to the `Reach and Average Frequency endpoint <https://developer.twitter.com/en/docs/ads/analytics/api-reference/reach>`__. These reports return performance data with a focus on reach and frequency metrics, that **cannot be aggregated over time** (*e.g. the reach of day A and B is not equal to the reach of day A + the reach of day B, as it counts unique individuals*). Output data **cannot be splitted by day** when requested over a larger time period. These reports are available **only for the Funding Instrument and Campaign entities**.
- **ENTITY reports**, making calls to `Campaign Management endpoints <https://developer.twitter.com/en/docs/ads/campaign-management/api-reference>`__ if the selected entity is Funding Instrument, Campaign, Line Item, Media Creative or Promoted Tweet, and to the `Creative endpoint <https://developer.twitter.com/en/docs/ads/creatives/api-reference/>`__ if the selected entity is Card. These reports return details on entity configuration since the creation of the Twitter Ads account.

*Call example for ANALYTICS reports*: this call will collect engagement metrics for Line Item entities, splitting the results by day, from 2020-01-01 to 2020-01-03:

.. code-block:: shell

    python nck/entrypoint.py read_twitter --twitter-consumer-key <API_KEY> --twitter-consumer-secret <API_SECRET_KEY> --twitter-access-token <ACCESS_TOKEN> --twitter-access-token-secret <ACCESS_TOKEN_SECRET> --twitter-account-id <ACCOUNT_ID> --twitter-report-type ANALYTICS --twitter-entity LINE_ITEM --twitter-metric-group ENGAGEMENT --twitter-segmentation-type AGE --twitter-granularity DAY --twitter-start-date 2020-01-01 --twitter-end-date 2020-01-03 write_console

*Call example for REACH reports*: this call will collect reach metrics (*total_audience_reach, average_frequency*) for Campaign entities, from 2020-01-01 to 2020-01-03:

.. code-block:: shell

    python nck/entrypoint.py read_twitter --twitter-consumer-key <API_KEY> --twitter-consumer-secret <API_SECRET_KEY> --twitter-access-token <ACCESS_TOKEN> --twitter-access-token-secret <ACCESS_TOKEN_SECRET> --twitter-account-id <ACCOUNT_ID> --twitter-report-type REACH --twitter-entity CAMPAIGN --twitter-start-date 2020-01-01 --twitter-end-date 2020-01-03 write_console

*Call example for ENTITY reports*: this call collects details on the configuration of Campaign entities (id, name, total_budget_amount_local_micro, currency), since the creation of the Twitter Ads account:

.. code-block:: shell

    python nck/entrypoint.py read_twitter --twitter-consumer-key <API_KEY> --twitter-consumer-secret <API_SECRET_KEY> --twitter-access-token <ACCESS_TOKEN> --twitter-access-token-secret <ACCESS_TOKEN_SECRET> --twitter-account-id <ACCOUNT_ID> --twitter-report-type REACH --twitter-entity CAMPAIGN --twitter-entity-attribute id --twitter-entity-attribute name --twitter-entity-attribute total_budget_amount_local_micro --twitter-entity-attribute currency write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_twitter``

---------------
Command options
---------------

==========================================  =================================================================================================================================================================================================================================
Options                                     Definition
==========================================  =================================================================================================================================================================================================================================
``--twitter-consumer-key``                  API key, available in the 'Keys and tokens' section of your Twitter Developer App.
``--twitter-consumer-secret``               API secret key, available in the 'Keys and tokens' section of your Twitter Developer App.
``--twitter-access-token``                  Access token, available in the 'Keys and tokens' section of your Twitter Developer App.
``--twitter-access-token-secret``           Access token secret, available in the 'Keys and tokens' section of your Twitter Developer App.
``--twitter-account-id``                    Specifies the Twitter Account ID for which the data should be returned.
``--twitter-report-type``                   Specifies the type of report to collect. Possible values: ANALYTICS, REACH, ENTITY.
``--twitter-entity``                        Specifies the entity type to retrieve data for. Possible values: FUNDING_INSTRUMENT, CAMPAIGN, LINE_ITEM, MEDIA_CREATIVE, PROMOTED_TWEET, CARD.
``--twitter-entity-attribute``              Specific to ENTITY reports. Specifies the entity attribute (configuration detail) that should be returned. To get possible values, print the ENTITY_ATTRIBUTES variable on nck/helpers/twitter_helper.py
``--twitter-granularity``                   Specific to ANALYTICS reports. Specifies how granular the retrieved data should be. Possible values: TOTAL (default), DAY.
``--twitter-metric-group``                  Specific to ANALYTICS reports. Specifies the list of metrics (as a group) that should be returned. Possible values can be found `here <https://developer.twitter.com/en/docs/ads/analytics/overview/metrics-and-segmentation>`__.
``--twitter-placement``                     Specific to ANALYTICS reports. Scopes the retrieved data to a particular placement. Possible values: ALL_ON_TWITTER (default), PUBLISHER_NETWORK.
``--twitter-segmentation-type``             Specific to ANALYTICS reports. Specifies how the retrieved data should be segmented. Possible values can be found `here <https://developer.twitter.com/en/docs/ads/analytics/overview/metrics-and-segmentation>`__.
``--twitter-platform``                      Specific to ANALYTICS reports. Required if segmentation_type is set to DEVICES or PLATFORM_VERSION. Possible values can be identified through the targeting_criteria/locations
``--twitter-country``                       Specific to ANALYTICS reports. Required if segmentation_type is set to CITIES, POSTAL_CODES, or REGION. Possible values can be identified through the GET targeting_criteria/platforms endpoint.
``--twitter-start-date``                    Start date of the period to request (format: YYYY-MM-DD).
``--twitter-end-date``                      End date of the period to request (format: YYYY-MM-DD).
``--twitter-add-request-date-to-report``    If set to True (default: False), the date on which the request is made will appear on each report record.
==========================================  =================================================================================================================================================================================================================================

If you need any further information, the documentation of Twitter Ads API can be found `here <https://developer.twitter.com/en/docs/ads/general/overview>`__. To get a better understanding of **Twitter Ads Hierrarchy and Terminology**, we advise you to have a look at `this page <https://developer.twitter.com/en/docs/tutorials/ads-api-hierarchy-terminology>`__.

==============
Yandex Readers
==============

----------
Source API
----------

`Yandex Direct API <https://tech.yandex.com/direct/>`__

-------------------------
How to obtain credentials
-------------------------

In order to access Yandex Direct API, you need two accounts: an advertiser account and a developer account.
Here is the process:

1. Create a developer account if you don't already have one. Click on the *Get started* button on this `page <https://direct.yandex.com/>`__.
2. Create and register an app that will access Yandex Direct API via `Yandex OAuth <https://oauth.yandex.com/client/new>`__.
3. Keep app client id safe. Log in with your advertiser account and `give permission to the app to access your data <https://tech.yandex.com/oauth/doc/dg/tasks/get-oauth-token-docpage/>`__.
4. Store your token very carefully.
5. Log out and log in as a developer and `ask permission to access Yandex Direct API <https://direct.yandex.com/registered/main.pl?cmd=apiSettings>`__ (ask for Full access). Fill in the form.
6. Wait for Yandex support to reply but it should be within a week.

======================
Yandex Campaign Reader
======================

`Official documentation <https://tech.yandex.com/direct/doc/ref-v5/campaigns/get-docpage/>`__

----------
Quickstart
----------

The following command retrieves the daily budget of all your campaigns, since your account creation.

.. code-block:: shell

    python nck/entrypoint.py read_yandex_campaigns --yandex-token <TOKEN> --yandex-field-name Id --yandex-field-name Name --yandex-field-name DailyBudget write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_yandex_campaigns``

---------------
Command options
---------------

======================================  ========================================================================================================================================================================
Options                                 Definition
======================================  ========================================================================================================================================================================
``--yandex-token``                      Bear token that allows you to authenticate to the API
``--yandex-campaign-id``                (Optional) Selects campaigns with the specified IDs.
``--yandex-campaign-state``             (Optional) Selects campaigns with the specified states. Possible values can be found `here <https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status>`__.
``--yandex-campaign-status``            (Optional) Selects campaigns with the specified statuses. Possible values can be found `here <https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status>`__.
``--yandex-campaign-payment-status``    (Optional) Selects campaigns with the specified payment `statuses <https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status>`__.
``--yandex-field-name``                 Parameters to get that are common to all types of campaigns.
======================================  ========================================================================================================================================================================

========================
Yandex Statistics Reader
========================

`Official documentation <https://tech.yandex.com/direct/doc/reports/reports-docpage/>`__

----------
Quickstart
----------

The following command retrieves a performance report for all your campaigns, since your account creation.

.. code-block:: shell

    python nck/entrypoint.py read_yandex_statistics --yandex-token <TOKEN> --yandex-report-type AD_PERFORMANCE_REPORT --yandex-field-name AdFormat --yandex-field-name AdId --yandex-field-name Impressions --yandex-include-vat True --yandex-report-language en --yandex-field-name AdGroupName --yandex-field-name AdGroupId --yandex-field-name AdNetworkType --yandex-field-name CampaignId --yandex-field-name CampaignName --yandex-field-name CampaignType --yandex-field-name Date --yandex-field-name Device --yandex-field-name Clicks --yandex-field-name Conversions --yandex-field-name Cost --yandex-date-range ALL_TIME write_console

*Didn't work?* See the `Troubleshooting`_ section.

------------
Command name
------------

``read_yandex_statistics``

---------------
Command options
---------------

Detailed version `here <https://tech.yandex.com/direct/doc/reports/spec-docpage/>`__.

==============================  =====================================================================================================================================================================
Options                         Definition
==============================  =====================================================================================================================================================================
``--yandex-token``              Bear token that allows you to authenticate to the API
``--yandex-report-language``    (Optional) Language of the report. Possible values can be found `here <https://tech.yandex.com/direct/doc/dg/concepts/headers-docpage/#headers__accept-language>`__.
``--yandex-filter``             (Optional) Filters on a particular field.
``--yandex-max-rows``           (Optional) The maximum number of rows in the report.
``--yandex-field-name``         Information you want to collect. Possible values can be found `here <https://tech.yandex.com/direct/doc/reports/fields-list-docpage/>`__.
``--yandex-report-type``        Type of report. Linked to the fields you want to select.
``--yandex-date-range``         Possible values can be found `here <https://tech.yandex.com/direct/doc/reports/period-docpage/>`__.
``--yandex-include-vat``        Adds VAT to your expenses if set to True
``--yandex-date-start``         (Optional) Selects data on a specific period of time. Combined with ``--yandex-date-stop`` and  ``--yandex-date-range`` set to CUSTOM_DATE.
``--yandex-date-stop``          (Optional) Selects data on a specific period of time. Combined with ``--yandex-date-start`` and  ``--yandex-date-range`` set to CUSTOM_DATE.
==============================  =====================================================================================================================================================================

===============
Troubleshooting
===============

You encountered an issue when running a Reader command and you don't know what's going on?
You may find an answer in the troubleshooting guide below.

1. Have you installed NCK dependencies? In order to run NCK, you need to install all dependencies. First create a `virtual environment <https://docs.python.org/3/library/venv.html>`__ and then run ``pip install -r requirements.txt``.
2. Have you set ``PYTHONPATH`` environment variable to the root of NCK folder?
3. Have you checked logs? The code has been implemented so that every error is logged.
