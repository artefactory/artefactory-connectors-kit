# NCK Readers

Each reader role is to read data from external source and transform it into a Stream understable format to be written on GCS and BQ thanks to the corresponding writers.

## List of Readers

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
- The Trade Desk
- Twitter Ads
- Yandex Campaign
- Yandex Statistics

## Step to create a new Reader

1. Create python module following naming nomenclature ``` [command]_reader.py ```
2. Implement `read` method
3. Create click command with required options
4. Reference click command into [commands list](./__init__.py)
5. Update current README.md

## Adobe Analytics Readers

As of May 2020 (last update of this section of the documentation), **two versions of Adobe Analytics Reporting API are  coexisting: 1.4 and 2.0**. As some functionalities of API 1.4 have not been made available in API 2.0 yet (Data Warehouse reports in particular), our Adobe Analytics Readers are also available in these two versions.

#### How to obtain credentials

Both Adobe Analytics Readers use the **JWT authentication framework**.
- Get developer access to Adobe Analytics (documentation can be found [here](https://helpx.adobe.com/enterprise/using/manage-developers.html))
- Create a Service Account integration to Adobe Analytics on [Adobe Developer Console](https://console.adobe.io/)
- Use the generated JWT credentials (Client ID, Client Secret, Technical Account ID, Organization ID and private.key file) to retrieve your Global Company ID (to be requested to [Discovery API](https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/discovery.md)). All these parameters will be passed to Adobe Analytics Readers.

### Adobe Analytics Reader 1.4

#### Source API

[Analytics API v1.4](https://github.com/AdobeDocs/analytics-1.4-apis)

#### Quickstart

Call example to Adobe Analytics Reader 1.4, getting the number of visits per day and tracking code for a specified Report Suite, between 2020-01-01 and 2020-01-31:

```
python nck/entrypoint.py read_adobe --adobe-client-id <CLIENT_ID> --adobe-client-secret <CLIENT_SECRET> --adobe-tech-account-id <TECH_ACCOUNT_ID> --adobe-org-id <ORG_ID> --adobe-private-key <PRIVATE_KEY> --adobe-global-company-id <GLOBAL_COMPANY_ID> --adobe-report-suite-id <REPORT_SUITE_ID> --adobe-date-granularity day --adobe-report-element-id trackingcode --adobe-report-metric-id visits --adobe-start-date 2020-01-01 --adobe-end-date 2020-01-31 write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

|CLI option|Documentation|
|--|--|
|`--adobe-client-id`|Client ID, that you can find on Adobe Developer Console|
|`--adobe-client-secret`|Client Secret, that you can find on Adobe Developer Console|
|`--adobe-tech-account-id`|Technical Account ID, that you can find on Adobe Developer Console|
|`--adobe-org-id`|Organization ID, that you can find on Adobe Developer Console|
|`--adobe-private-key`|Content of the private.key file, that you had to provide to create the integration. Make sure to enter the parameter in quotes, include headers, and indicate newlines as \n.|
|`--adobe-global-company-id`|Global Company ID (to be requested to [Discovery API](https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/discovery.md))|
|`--adobe-list-report-suite`|Should be set to *True* if you wish to request the list of available Adobe Report Suites (*default: False*). If set to *True*, the below parameters should be left empty.|
|`--adobe-report-suite-id`|ID of the requested Adobe Report Suite|
|`--adobe-report-element-id`|ID of the element (i.e. dimension) to include in the report|
|`--adobe-report-metric-id`|ID of the metric to include in the report|
|`--adobe-date-granularity`|Granularity of the report. *Possible values: PREVIOUS_DAY, LAST_30_DAYS, LAST_7_DAYS, LAST_90_DAYS*|
|`--adobe-start-date`|Start date of the period to request (format: YYYY-MM-DD)|
|`--adobe-end-date`|End date of the period to request (format: YYYY-MM-DD)|

#### Addtional information

- **The full list of available elements and metrics** can be retrieved with the [GetElements](https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/reporting-api/methods/r_GetElements.md) and [GetMetrics](https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/reporting-api/methods/r_GetMetrics.md) methods.
- **Adobe Analytics Reader 1.4 requests Data Warehouse reports** (the "source" parameter is set to "warehouse" in the report description), allowing it to efficiently process multiple-dimension requests.
- **If you need further information**, the documentation of Adobe APIs 1.4 can be found [here](https://github.com/AdobeDocs/analytics-1.4-apis).

### Adobe Analytics Reader 2.0

#### Source API

[Analytics API v2.0](https://github.com/AdobeDocs/analytics-2.0-apis)

#### Quickstart

Call example to Adobe Analytics Reader 2.0, getting the number of visits per day and tracking code for a specified Report Suite, between 2020-01-01 and 2020-01-31:

```
python nck/entrypoint.py read_adobe_2_0 --adobe-2-0-client-id <CLIENT_ID> --adobe-2-0-client-secret <CLIENT_SECRET> --adobe-2-0-tech-account-id <TECH_ACCOUNT_ID> --adobe-2-0-org-id <ORG_ID> --adobe-2-0-private-key <PRIVATE_KEY> --adobe-2-0-global-company-id <GLOBAL_COMPANY_ID> --adobe-2-0-report-suite-id <REPORT_SUITE_ID> --adobe-2-0-dimension daterangeday --adobe-2-0-dimension campaign --adobe-2-0-start-date 2020-01-01 --adobe-2-0-end-date 2020-01-31 --adobe-2-0-metric visits write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

|CLI option|Documentation|
|--|--|
|`--adobe-2-0-client-id`|Client ID, that you can find on Adobe Developer Console|
|`--adobe-2-0-client-secret`|Client Secret, that you can find on Adobe Developer Console|
|`--adobe-2-0-tech-account-id`|Technical Account ID, that you can find on Adobe Developer Console|
|`--adobe-2-0-org-id`|Organization ID, that you can find on Adobe Developer Console|
|`--adobe-2-0-private-key`|Content of the private.key file, that you had to provide to create the integration. Make sure to enter the parameter in quotes, include headers, and indicate newlines as \n.|
|`--adobe-2-0-global-company-id`|Global Company ID (to be requested to [Discovery API](https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/discovery.md))|
|`--adobe-2-0-report-suite-id`|ID of the requested Adobe Report Suite|
|`--adobe-2-0-dimension`|Dimension to include in the report|
|`--adobe-2-0-metric`|Metric to include in the report|
|`--adobe-2-0-start-date`|Start date of the period to request (format: YYYY-MM-DD)|
|`--adobe-2-0-end-date`|Start date of the period to request (format: YYYY-MM-DD)|

#### Additional information

- **In API 2.0, dimension and metric names are slightly different from API 1.4**. To get new metric and dimension names and reproduce the behavior of Adobe Analytics UI as closely as possible, [enable the Debugger feature in Adobe Analytics Workspace](https://github.com/AdobeDocs/analytics-2.0-apis/blob/master/reporting-tricks.md): it allow you to visualize the back-end JSON requests made by Adobe Analytics UI to Reporting API 2.0.
-  **In API 2.0, the date granularity parameter was removed, and should now be handled as a dimension**: a request featuring `--adobe-dimension daterangeday` will produce a report with a day granularity.
- **API 2.0 does not feature Data Warehouse reports yet** (along with other features, that are indicated on the "Current limitations" section of [this page](https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/migration-guide.md)). For this reason, if you wish to collect multiple-dimension reports, Adobe Analytics Reader 1.4 might be a more efficient solution in terms of processing time. 
- **If you need any further information**, the documentation of Adobe APIs 2.0 can be found [here](https://github.com/AdobeDocs/analytics-2.0-apis).

## Amazon S3 Reader

*Not documented yet.*

## Facebook Marketing Reader

#### Source API

[Facebook Marketing API](https://developers.facebook.com/docs/marketing-api/reference/v7.0)

#### Quickstart

The Facebook Marketing Reader handles calls to 2 endpoints of the Facebook Marketing API: **Facebook Ad Insights** (to retrieve performance data), and **Facebook Ad Management** (to retrieve configuration data).

*Example of Ad Insights Request*
```
python nck/entrypoint.py read_facebook --facebook-access-token <ACCESS_TOKEN> --facebook-object-id <OBJECT_ID> --facebook-breakdown age --facebook-breakdown gender --facebook-action-breakdown action_type --facebook-field ad_id --facebook-field ad_name --facebook-field impressions --facebook-field clicks --facebook-field actions[action_type:post_engagement] --facebook-field actions[action_type:video_view] --facebook-field age --facebook-field gender --facebook-time-increment 1 --facebook-start-date 2020-01-01 --facebook-end-date 2020-01-03 write_console
```

*Example of Ad Management Request*
```
python nck/entrypoint.py read_facebook --facebook-access-token <ACCESS_TOKEN> --facebook-object-id <OBJECT_ID>  --facebook-ad-insights False --facebook-level ad --facebook-field id --facebook-field creative[id] --facebook-add-date-to-report True --facebook-start-date 2020-01-01 --facebook-end-date 2019-01-01 write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

|CLI option|Documentation|
|:--|:--|
|`--facebook-app-id`|Facebook App ID. *Not mandatory if Facebook Access Token is provided.*|
|`--facebook-app-secret`|Facebook App Secret. *Not mandatory if Facebook Access Token is provided.*|
|`--facebook-access-token`|Facebook App Access Token.|
|`--facebook-object-type`|Nature of the root Facebook Object used to make the request. *Possible values: creative (available only for Ad Management requests), ad, adset, campaign, account (default).*|
|`--facebook-object-id`|ID of the root Facebook Object used to make the request.|
|`--facebook-level`|Granularity of the response. *Possible values: creative (available only for Ad Management requests), ad (default), adset, campaign, account.*|
|`--facebook-ad-insights`|*True* (default) if *Ad Insights* request, *False* if *Ad Management* request.|
|`--facebook-field`|Fields to be retrieved.|
|`--facebook-start-date`|Start date of the period to request (format: YYYY-MM-DD). *This parameter is only relevant for Ad Insights Requests, and Ad Management requests at the Campaign, Adset and Ad levels.*|
|`--facebook-end-date`|Start date of the period to request (format: YYYY-MM-DD). *This parameter is only relevant for Ad Insights Requests, and Ad Management requests at the Campaign, Adset and Ad levels.*|
|`--facebook-date-preset`|Relative time range. Ignored if *--facebook-start date* and *--facebook-end-date* are specified. *This parameter is only relevant for Ad Insights Requests, and Ad Management requests at the Campaign, Adset and Ad levels.*|
|`--facebook-time-increment`|Cuts the results between smaller time slices within the specified time range. *This parameter is only relevant for Ad Insights Requests, and Ad Management requests at the Campaign, Adset and Ad levels.*|
|`--facebook-add-date-to-report`|*True* if you wish to add the date of the request to each response record, *False* otherwise (default).|
|`--facebook-breakdown`|How to break down the result. *This parameter is only relevant for Ad Insights Requests.*|
|`--facebook-action-breakdown`|How to break down action results. *This parameter is only relevant for Ad Insights Requests.*|

#### Additional information

**1. Make sure to select the appropriate `--facebook-level`**

|If Facebook Object Type is...|Facebook Level can be...|
|:--|:--|
|`account`|account, campaign, adset, ad, creative|
|`campaign`|campaign, adset, ad|
|`adset`|adset, ad, creative|
|`ad`|ad, creative|
|`creative`|creative|

**2. Format Facebook Marketing Reader response using `--facebook-fields`**

2.1. The list of **applicable fields** can be found on the links below:

- **Ad Insights Request**: [all fields](https://developers.facebook.com/docs/marketing-api/insights/parameters/v7.0)
- **Ad Management Request**: [Account-level fields](https://developers.facebook.com/docs/marketing-api/reference/ad-account), [Campaign-level fields](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group), [Adset-level fields](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign), [Ad-level fields](https://developers.facebook.com/docs/marketing-api/reference/adgroup), [Creative-level fields](https://developers.facebook.com/docs/marketing-api/reference/ad-creative)

2.2. If you want to select **a nested field value**,  simply indicate the path to this value within the request field.

*Facebook Marketing Reader Request*
```
--facebook-field object_story_spec[video_data][call_to_action][value][link]
```

*API Response*
```
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
```

*Facebook Marketing Reader Response*
```
{"object_story_spec_video_data_call_to_action_value_link": "https://www.artefact.com"}
```

2.3 **Action Breakdown filters** can be applied to the fields of ***Ad Insights* Requests** using the following syntax: <FIELD_NAME>[<ACTION_BREAKDOWN>:<ACTION_BREAKDOWN_VALUE>]. You can combine multiple Action Breakdown filters on the same field by adding them in cascade next to each other.

*Facebook Marketing Reader Request*
```
--facebook-action-breakdown action_type
--facebook-field actions[action_type:video_view][action_type:post_engagement]
```

*API Response*
```
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

```
*Facebook Marketing Reader Response*
```
{"actions_action_type_video_view": "17", "actions_action_type_post_engagement": "25"}
```

## Google Readers

### Authentication

You can authenticate to most of the Readers of the Google Suite following the same schema. You'll need to generate a **refresh token** to connect via the OAuth flow. A full script to do this can be found in this [refresh token generator](https://github.com/artefactory/Refresh-token-generator-for-google-oauth).

### Google Ads Reader

#### Source API

[AdWords API](https://developers.google.com/adwords/api/docs/guides/start)

#### How to obtain credentials

Using the AdWords API requires four things:
- A developer token (Generated at a company level - one per company -, takes around 2 days to be approved by Google) which can be completely independant from the Google Ads Account you will be calling (though you need a Manager Google Ads Account to request a token for your company)
- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>
- A refresh token, created with the email address able to access to all the Google Ads Account you will be calling
- The ID of the Google Ads Accounts <CLIENT_CUSTOMER_ID> you will be reading from (XXX-XXX-XXXX numbers, written right next to your Account Name)

See the [documentation here](https://developers.google.com/adwords/api/docs/guides/signup) to apply for access if your Company does not already have a developer token (granting you the right to use the API).

See the [documentation here](https://developers.google.com/adwords/api/docs/guides/first-api-call) to set-up your OAuth2 credentials and refresh token specifically for your Google Ads Accounts.

#### Quickstart

The following command retrieves insights about the Ads of *my_first_campaign* and *my_second_campaign* in the Google Ads Account <CLIENT_CUSTOMER_ID>, thanks to your company <DEVELOPER_TOKEN>, <CLIENT_ID>, <CLIENT_SECRET> and <REFRESH_TOKEN> with the necessary permissions to access your Accounts.

```
python nck/entrypoint.py read_googleads --googleads-developer-token <DEVELOPER_TOKEN> --googleads-client-id <CLIENT_ID> --googleads-client-secret <CLIENT_SECRET> --googleads-refresh-token <REFRESH_TOKEN> --googleads-client-customer-id <XXX-XXX-XXXX CLIENT_CUSTOMER_ID> --googleads-report-type AD_PERFORMANCE_REPORT --googleads-date-range-type LAST_7_DAYS --googleads-field CampaignName --googleads-field AdGroupName --googleads-field Headline --googleads-field Date --googleads-field Impressions --googleads-report-filter "{'field':'CampaignName','operator':'IN','values':['my_first_campaign','my_second_campaign']}"
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

|CLI option|Documentation|
|--|--|
|`--googleads-developer-token`|Company Developer token for Google Ads API|
|`--googleads-client-id`|OAuth2 ID|
|`--googleads-client-secret`|OAuth2 secret|
|`--googleads-refresh-token`|Refresh token for OAuth2|
|`--googleads-manager-id`|(Optional) Manager_Account_ID (XXX-XXX-XXXX identifier)|
|`--googleads-client-customer-id`|GAds_Account_ID (ignored if a manager account ID was given)|
|`--googleads-report-name`|(Optional) Name of your output stream ("Custom Report" by default)|
|`--googleads-report-type`|Type of report to be called|
|`--googleads-date-range-type`|Type of date range to apply (if "CUSTOM_RANGE", a min and max date must be specified). *Possible values can be found [here](https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges).*|
|`--googleads-start-date`|(Optional) Start date for "CUSTOM_RANGE" date range (format: YYYY-MM-DD)|
|`--googleads-end-date`|(Optional) End date for "CUSTOM_RANGE" date range (format: YYYY-MM-DD)|
|`--googleads-field`|Fields to include in the report|
|`--googleads-report-filter`|Filter to apply on a chosen field (Dictionary as String "{'field':,'operator':,'values':}")|
|`--googleads-include-zero-impressions`|Boolean specifying whether or not rows with zero impressions should be included in the report|
|`--googleads-filter-on-video-campaigns`|Boolean used to filter the report on Video Campaigns only (require CampaignId to be listed as a field)|
|`--googleads-include-client-customer-id`|Boolean used to add "AccountId" as a field in the output stream. *AccountId is not available in the API, but is known since it's a requirement to call the API (= Client Customer ID)*|

See documentation below for a better understanding of the parameters:
- [Reporting basics](https://developers.google.com/adwords/api/docs/guides/reporting#create_a_report_definition)
- [Available reports and associated fields](https://developers.google.com/adwords/api/docs/appendix/reports#available-reports)

### Google Analytics Reader

#### Source API

[Analytics Reporting API](https://developers.google.com/analytics/devguides/reporting/core/v4)

#### Quickstart

The following command retrieves sessions, pageviews and bounces volumes by date from 2020-01-01 to 2020-01-03, for the Analytics View <VIEW_ID>, thanks your <CLIENT_ID>, <CLIENT_SECRET> and <REFRESH_TOKEN> with the necessary permissions to access your accounts.

```
python nck/entrypoint.py read_ga --ga-client-id <CLIENT_ID> --ga-client-secret <CLIENT_SECRET> --ga-view-id <VIEW_ID> --ga-refresh-token <REFRESH_TOKEN> --ga-dimension ga:date --ga-metric sessions --ga-metric ga:pageviews --ga-metric ga:bounces --ga-start-date 2020-01-01 --ga-end-date 2020-01-03 write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

|CLI option|Documentation|
|--|--|
|`--ga-client-id`|OAuth2 ID|
|`--ga-client-secret`|OAuth2 secret|
|`--ga-access-token`|(Optional) Access token for OAuth2|
|`--ga-refresh-token`|Refresh token for OAuth2|
|`--ga-view-id`|Analytics View ID from which to retrieve data. See documentation [here](https://support.google.com/analytics/answer/1009618) for a better understanding of Google Analytics hierrarchy.|
|`--ga-account-id`|Analytics Account ID from which to retrieve data. See documentation [here](https://support.google.com/analytics/answer/1009618) for a better understanding of Google Analytics hierrarchy.|
|`--ga-dimension`|Dimensions to include in the report (max 9). Possible values can be found [here](https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/).|
|`--ga-metric`|Metrics to include in the report (min 1, max 10). Possible values can be found [here](https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/).|
|`--ga-segment-id`|Segment ID of a built-in or custom segment (for example gaid::-3) on which report data should be segmented.|
|`--ga-start-date`|Start date of the period to request (format: YYYY-MM-DD)|
|`--ga-end-date`|End date of the period to request (format: YYYY-MM-DD)|
|`--ga-date-range`|<START_DATE> <END_DATE> of the period to request, specified as a unique argument (format: YYYY-MM-DD YYYY-MM-DD)|
|`--ga-day-range`|Relative time range. *Possible values: PREVIOUS_DAY, LAST_30_DAYS, LAST_7_DAYS, LAST_90_DAYS.*|
|`--ga-sampling-level`|Desired sample size. See documentation [here](https://support.google.com/analytics/answer/2637192) for a better understanding of Google Analytics sampling. *Possible values: SMALL, DEFAULT, LARGE (default).*|
|`--ga-add-view`|If set to *True* (default: False)*, adds a "ga:viewId" field to the output stream.|

See documentation [here](https://developers.google.com/analytics/devguides/reporting/core/v4/basics) for a better understanding of the parameters.

### Google Cloud Storage Reader

*Not documented yet.*

### Google Campaign Manager Reader

#### Source API

[DCM/DFA Reporting and Trafficking API](https://developers.google.com/doubleclick-advertisers/v3.3)

#### Quickstart

The following command retrieves impressions, clicks and cost volumes from 2020-01-01 to 2020-01-03, thanks your <CLIENT_ID>, <CLIENT_SECRET>, <REFRESH_TOKEN> and <PROFILE_ID> with the necessary permissions to access your accounts.

```
python nck/entrypoint.py read_dcm --dcm-client-id <CLIENT_ID> --dcm-client-secret <CLIENT_SECRET> --dcm-refresh-token <REFRESH_TOKEN> --dcm-profile-id <PROFILE_ID> --dcm-dimension dfa:date --dcm-metric dfa:impressions --dcm-metric dfa:clicks --dcm-metric dfa:mediaCost --dcm-start-date 2020-01-01 --dcm-end-date 2020-01-03 write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

##### Parameters

|CLI option|Documentation|
|--|--|
|`--dcm-client-id`|OAuth2 ID|
|`--dcm-client-secret`|OAuth2 secret|
|`--dcm-access-token`|(Optional) Access token for OAuth2|
|`--dcm-refresh-token`|Refresh token for OAuth2|
|`--dcm-profile-id`|ID of the DFA user profile that has been granted permissions to the CM account for which you want to retrieve data. You should have 1 DFA user profile per CM account that you can access. The associated ID can be found directly on your Campaign Manager UI (when accessing your list of CM accounts, on the top right hand corner).|
|`--dcm-report-name`|Name of the report, that will appear in CM UI.|
|`--dcm-report-type`|Type of the report. *Possible values: CROSS_DIMENSION_REACH, FLOODLIGHT, PATH_TO_CONVERSION, REACH, STANDARD.*|
|`--dcm-dimension`|Dimensions to include in the report. *Possible values can be found [here](https://developers.google.com/doubleclick-advertisers/v3.3/dimensions).*|
|`--dcm-metric`|Metrics to include in the report. *Possible values can be found [here](https://developers.google.com/doubleclick-advertisers/v3.3/dimensions).*|
|`--dcm-filter`|<FILTER_TYPE> <FILTER_VALUE> association, used to narrow the scope of the report. For instance "dfa:advertiserId XXXXX" will narrow report scope to the performance of Advertiser ID XXXXX. *Possible filter types can be found [here](https://developers.google.com/doubleclick-advertisers/v3.3/dimensions).*|
|`--dcm-start-date`|Start date of the period to request (format: YYYY-MM-DD)|
|`--dcm-end-date`|End date of the period to request (format: YYYY-MM-DD)|

### Google Display & Video 360 Reader

#### Source API

[Doubleclick Bid Manager API](https://developers.google.com/bid-manager/v1)

#### Quickstart

The following command retrieves impressions, clicks and cost volumes filtered on a specific <ADVERTISER_ID> from 2020-01-01 to 2020-01-03, thanks your <CLIENT_ID>, <CLIENT_SECRET> and <REFRESH_TOKEN> with the necessary permissions to access your accounts.

```
python nck/entrypoint.py read_dbm --dbm-client-id <CLIENT_ID> --dbm-client-secret <CLIENT_SECRET> —dbm-refresh-token <REFRESH_TOKEN> —dbm-filter FILTER_ADVERTISER <ADVERTISER_ID> --dbm-query-dimension FILTER_DATE  --dbm-query-metric METRIC_IMPRESSIONS --dbm-query-metric METRIC_CLICKS --dbm-query-metric METRIC_MEDIA_COST_ADVERTISER --dbm-query-param-type TYPE_GENERAL --dbm-request-type custom_query_report --dbm-start-date 2020-01-01 --dbm-end-date 2020-01-03 write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

|CLI option|Documentation|
|--|--|
|`--dbm-client-id`|OAuth2 ID|
|`--dbm-client-secret`|OAuth2 secret|
|`--dbm-access-token`|(Optional) Access token for OAuth2|
|`--dbm-refresh-token`|Refresh token for OAuth2|
|`--dbm-query-request-type`|Doubleclick Bid Manager API request type. *Possible values: existing_query, custom_query, existing_query_report, custom_query_report, lineitems_objects, sdf_objects and list_reports.*|
|`--dbm-query-id`|Query ID.|
|`--dbm-query-title`|Query title, used to name the reports generated from this query in DV360 UI.|
|`--dbm-query-frequency`|How often the query is run. *Possible values can be found [here](https://developers.google.com/bid-manager/v1/queries#schedule.frequency). Default: ONE_TIME.*|
|`--dbm-filter`|<FILTER_TYPE> <FILTER_VALUE> association, used to narrow the scope of the report. For instance "FILTER_ADVERTISER XXXXX" will narrow report scope to the performance of Advertiser ID XXXXX. *Possible filter types can be found [here](https://developers.google.com/bid-manager/v1/filters-metrics#filters).*|
|`--dbm-query-dimension`|Dimensions to include in the report. *Possible values can be found [here](https://developers.google.com/bid-manager/v1/filters-metrics#filters).*|
|`--dbm-query-metric`|Metrics to include in the report. *Possible values can be found [here](https://developers.google.com/bid-manager/v1/filters-metrics#metrics).*|
|`--dbm-query-param-type`|Report type. *Possible values can be found [here](https://developers.google.com/bid-manager/v1/queries#params.type). Default: TYPE_TRUEVIEW.*|
|`--dbm-start-date`|Start date of the period to request (format: YYYY-MM-DD)|
|`--dbm-end-date`|End date of the period to request (format: YYYY-MM-DD)|

### Google Search Console Reader

#### Source API

[Search Console API (Search Analytics endpoint)](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/)

#### How to obtain credentials

Using the Google Search Console API requires three main parameters:
- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>
- A refresh token, created with the email address able to access to your Google Search Console Account.
- The URLs whose performance you want to see

#### Quickstart

The following command retrieves insights about the URL <SITE_URL> from 2020-01-01 to 2020-01-03, thanks to your <CLIENT_ID> and <REFRESH_TOKEN> with the necessary permissions to access your accounts.

```
python nck/entrypoint.py read_search_console --search-console-client-id <CLIENT_ID> --search-console-refresh-token <REFRESH_TOKEN> --search-console-site-url <SITE_URL> --search-console-dimensions country --search-console-dimensions device --search-console-start-date 2020-01-01 --search-console-end-date 2020-01-03 write_console 
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

|CLI option|Documentation|
|--|--|
|`--search-console-client-id`|OAuth2 ID|
|`--search-console-client-secret`|OAuth2 secret|
|`--search-console-access-token`|Access token for OAuth2|
|`--search-console-refresh-token`|Refresh token for OAuth2|
|`--search-console-dimensions`|Dimensions of the report. *Possible values can be found [here](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query#dimensionFilterGroups.filters.dimension).*|
|`--search-console-site-url`|Site URL whose performance you want to request|
|`--search-console-start-date`|Start date of the period to request (format: YYYY-MM-DD)|
|`--search-console-end-date`|End date of the period to request (format: YYYY-MM-DD)|
|`--search-console-date-column`|If set to *True*, a date column will be included in the report|
|`--search-console-row-limit`|Row number by report page|

See documentation [here](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query) for a better understanding of the parameters.

### Google Search Ads 360 Reader

#### Source API

[Search Ads 360 API](https://developers.google.com/search-ads/v2/reference)

#### How to obtain credentials

Using the Search Ads API requires two things:
- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>
- A refresh token, created with the email address able to access to all the Search Ads 360 Account you will be calling

See the [documentation here](https://developers.google.com/search-ads/v2/authorizing "SA360 Authentication")
to set-up your OAuth2 credentials and refresh token specifically for Search Ads 360 Reporting.

#### Quickstart

The following command retrieves insights about the Ads in the Search Ads 360 Account <ADVERTISER_ID> from the agency <AGENCY_ID> thanks to your <CLIENT_ID>, <CLIENT_SECRET> and <REFRESH_TOKEN> with the necessary permissions to access your accounts.

```
python nck/entrypoint.py read_sa360 --sa360-client-id <CLIENT_ID> --sa360-client-secret <CLIENT_SECRET> --sa360-refresh-token <REFRESH_TOKEN> --sa360-agency-id <AGENCY_ID> --sa360-advertiser-id <ADVERTISER_ID> --sa360-report-type keyword --sa360-column date --sa360-column impr --sa360-column clicks --sa360-start-date 2020-01-01 --sa360-end-date 2020-01-01 
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

|CLI option|Documentation|
|--|--|
|`--sa360-client-id`|OAuth2 ID|
|`--sa360-client-secret`|OAuth2 secret|
|`--sa360-access-token`|(Optional) Access token|
|`--sa360-refresh-token`|Refresh token|
|`--sa360-agency-id`|Agency ID to request in SA360|
|`--sa360-advertiser-id`|(Optional) Advertiser ids to request. If not provided, every advertiser of the agency will be requested|
|`--sa360-report-name`|(Optional) Name of the output report|
|`--sa360-report-type`| Type of the report to request. *Possible values can be found [here](https://developers.google.com/search-ads/v2/report-types).*|
|`--sa360-column`|Dimensions and metrics to include in the report|
|`--sa360-saved-column`|(Optional) Saved columns to report. *Documentation can be found [here](https://developers.google.com/search-ads/v2/how-tos/reporting/saved-columns).*|
|`--sa360-start-date`|Start date of the period to request (format: YYYY-MM-DD)|
|`--sa360-end-date`|End date of the period to request (format: YYYY-MM-DD)|

See documentation [here](https://developers.google.com/search-ads/v2/how-tos/reporting) for a better understanding of the parameters.

### Google Sheets Reader

*Not documented yet.*

## Oracle Reader

*Not documented yet.*

## MySQL Reader

*Not documented yet.*

## Radarly Reader

*Not documented yet.*

## Salesforce Reader

*Not documented yet.*

## The Trade Desk Reader

#### How to obtain credentials

- Ask your Account Representative to **give you access to The Trade Desk API and UI**
- He will generally provide you with **two distinct accounts**:  an **API account**, allowing you to make API calls (*Login: ttd_api_{XXXXX}@client.com*), and a **UI account**, allowing you to navigate on The Trade Desk UI to create Report Templates (*Login: your professional e-mail address*)
- Pass **the Login and Password of your API account** to The Trade Desk connector

#### Quickstart

To request dimensions and metrics to The Trade Desk API, you should first **create a Report Template in The Trade Desk UI**, by following the below process:

- Connect to [The Trade Desk UI](https://desk.thetradedesk.com/) using the Login and Password of your UI account
- Navigate to *Reports* > *My Reports* to land on the *Report Templates* section
- Clone an existing Report Template, edit it to keep only the dimensions and metrics that you want to collect, and save it: it will appear under the *Mine* section
- Provide the exact name of the Report Template you have just created under the CLI option `--ttd-report-template-name` of The Trade Desk connector: the connector will "schedule" a report instance (which may take a few minutes to run), and fetch data to the location of your choice

The following command retrieves the data associated to the Report template named "*adgroup_performance_report*" between 2020-01-01 and 2020-01-03, filtered on the PartnerId <PARTNER_ID>:
```
python nck/entrypoint.py read_ttd --ttd-login <LOGIN> --ttd-password <PASSWORD> --ttd-partner-id <PARTNER_ID> --ttd-report-template-name adgroup_performance_report --ttd-start-date 2020-01-01  --ttd-end-date 2020-01-03 write_console
```
Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

|CLI option|Documentation|
|--|--|
|`--ttd-login`|Login of your API account|
|`--ttd-password`|Password of your API account|
|`--ttd-advertiser-id`|Advertiser Ids for which report data should be fetched|
|`--ttd-report-template-name`|Exact name of the Report Template to request. Existing Report Templates can be found within the [MyReports section](https://desk.thetradedesk.com/MyReports) of The Trade Desk UI.|
|`--ttd-report-schedule-name`|Name of the Report Schedule to create|
|`--ttd-start-date`|Start date of the period to request (format: YYYY-MM-DD)|
|`--ttd-end-date`|End date of the period to request (format: YYYY-MM-DD)|

If you need any further information, the documentation of The Trade Desk API can be found [here](https://api.thetradedesk.com/v3/portal/api/doc/ApiOverview).

## Twitter Ads Reader

#### Source API

[Twitter Ads API](https://developer.twitter.com/en/docs/ads/general/overview)

#### How to obtain credentials

* **Apply for a developer account** through [this link](https://developer.twitter.com/en/apply).
* **Create a Twitter app** on the developer portal: it will generate your authentication credentials.
* **Apply for Twitter Ads API access** by filling out [this form](https://developer.twitter.com/en/docs/ads/general/overview/adsapi-application). Receiving Twitter approval may take up to 7 business days.
* **Get access to the Twitter Ads account** you wish to retrieve data for, on the @handle that you used to create your Twitter App. Be careful, access levels matter: with an *Ad Manager* access, you will be able to request all report types; with a *Campaign Analyst* access, you will be able to request all report types, except ENTITY reports on Card entities.

#### Quickstart

The Twitter Ads Reader can collect **3 types of reports**, making calls to 4 endpoints of the Twitter Ads API:
* **ANALYTICS reports**, making calls to the [Asynchronous Analytics endpoint](https://developer.twitter.com/en/docs/ads/analytics/api-reference/asynchronous). These reports return performance data for a wide range of metrics, that **can be aggregated over time**. Output data **can be splitted by day** when requested over a larger time period.
* **REACH reports**, making calls to the [Reach and Average Frequency endpoint](https://developer.twitter.com/en/docs/ads/analytics/api-reference/reach). These reports return performance data with a focus on reach and frequency metrics, that **cannot be aggregated over time** (*e.g. the reach of day A and B is not equal to the reach of day A + the reach of day B, as it counts unique individuals*). Output data **cannot be splitted by day** when requested over a larger time period. These reports are available **only for the Funding Instrument and Campaign entities**.
* **ENTITY reports**, making calls to [Campaign Management endpoints](https://developer.twitter.com/en/docs/ads/campaign-management/api-reference) if the selected entity is Funding Instrument, Campaign, Line Item, Media Creative or Promoted Tweet, and to the [Creative endpoint](https://developer.twitter.com/en/docs/ads/creatives/api-reference/) if the selected entity is Card. These reports return details on entity configuration since the creation of the Twitter Ads account.

*Call example for ANALYTICS reports*: this call will collect engagement metrics for Line Item entities, splitting the results by day, from 2020-01-01 to 2020-01-03:
```
python nck/entrypoint.py read_twitter --twitter-consumer-key <API_KEY> --twitter-consumer-secret <API_SECRET_KEY> --twitter-access-token <ACCESS_TOKEN> --twitter-access-token-secret <ACCESS_TOKEN_SECRET> --twitter-account-id <ACCOUNT_ID> --twitter-report-type ANALYTICS --twitter-entity LINE_ITEM --twitter-metric-group ENGAGEMENT --twitter-segmentation-type AGE --twitter-granularity DAY --twitter-start-date 2020-01-01 --twitter-end-date 2020-01-03 write_console
```

*Call example for REACH reports*: this call will collect reach metrics (*total_audience_reach, average_frequency*) for Campaign entities, from 2020-01-01 to 2020-01-03:
```
python nck/entrypoint.py read_twitter --twitter-consumer-key <API_KEY> --twitter-consumer-secret <API_SECRET_KEY> --twitter-access-token <ACCESS_TOKEN> --twitter-access-token-secret <ACCESS_TOKEN_SECRET> --twitter-account-id <ACCOUNT_ID> --twitter-report-type REACH --twitter-entity CAMPAIGN --twitter-start-date 2020-01-01 --twitter-end-date 2020-01-03 write_console
```

*Call example for ENTITY reports*: this call collects details on the configuration of Campaign entities (id, name, total_budget_amount_local_micro, currency), since the creation of the Twitter Ads account:
```
python nck/entrypoint.py read_twitter --twitter-consumer-key <API_KEY> --twitter-consumer-secret <API_SECRET_KEY> --twitter-access-token <ACCESS_TOKEN> --twitter-access-token-secret <ACCESS_TOKEN_SECRET> --twitter-account-id <ACCOUNT_ID> --twitter-report-type REACH --twitter-entity CAMPAIGN --twitter-entity-attribute id --twitter-entity-attribute name --twitter-entity-attribute total_budget_amount_local_micro --twitter-entity-attribute currency write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

|CLI option|Documentation|
|--|--|
|`--twitter-consumer-key`|API key, available in the 'Keys and tokens' section of your Twitter Developer App.|
|`--twitter-consumer-secret`|API secret key, available in the 'Keys and tokens' section of your Twitter Developer App.|
|`--twitter-access-token`|Access token, available in the 'Keys and tokens' section of your Twitter Developer App.|
|`--twitter-access-token-secret`|Access token secret, available in the 'Keys and tokens' section of your Twitter Developer App.|
|`--twitter-account-id`|Specifies the Twitter Account ID for which the data should be returned.|
|`--twitter-report-type`|Specifies the type of report to collect. *Possible values: ANALYTICS, REACH, ENTITY.*|
|`--twitter-entity`|Specifies the entity type to retrieve data for. *Possible values: FUNDING_INSTRUMENT, CAMPAIGN, LINE_ITEM, MEDIA_CREATIVE, PROMOTED_TWEET, CARD.*|
|`--twitter-entity-attribute`|Specific to ENTITY reports. Specifies the entity attribute (configuration detail) that should be returned. *To get possible values, print the ENTITY_ATTRIBUTES variable on nck/helpers/twitter_helper.py*|
|`--twitter-granularity`|Specific to ANALYTICS reports. Specifies how granular the retrieved data should be. *Possible values: TOTAL (default), DAY.*|
|`--twitter-metric-group`|Specific to ANALYTICS reports. Specifies the list of metrics (as a group) that should be returned. *Possible values can be found [here](https://developer.twitter.com/en/docs/ads/analytics/overview/metrics-and-segmentation).* |
|`--twitter-placement`|Specific to ANALYTICS reports. Scopes the retrieved data to a particular placement. *Possible values: ALL_ON_TWITTER (default), PUBLISHER_NETWORK.*|
|`--twitter-segmentation-type`|Specific to ANALYTICS reports. Specifies how the retrieved data should be segmented. *Possible values can be found [here](https://developer.twitter.com/en/docs/ads/analytics/overview/metrics-and-segmentation).* |
|`--twitter-platform`|Specific to ANALYTICS reports. Required if segmentation_type is set to DEVICES or PLATFORM_VERSION. *Possible values can be identified through the targeting_criteria/locations*|
|`--twitter-country`|Specific to ANALYTICS reports. Required if segmentation_type is set to CITIES, POSTAL_CODES, or REGION. *Possible values can be identified through the GET targeting_criteria/platforms endpoint.*|
|`--twitter-start-date`|Start date of the period to request (format: YYYY-MM-DD).|
|`--twitter-end-date`|End date of the period to request (format: YYYY-MM-DD).|
|`--twitter-add-request-date-to-report`|If set to *True* (default: *False*), the date on which the request is made will appear on each report record.|

If you need any further information, the documentation of Twitter Ads API can be found [here](https://developer.twitter.com/en/docs/ads/general/overview). To get a better understanding of **Twitter Ads Hierrarchy and Terminology**, we advise you to have a look at [this page](https://developer.twitter.com/en/docs/tutorials/ads-api-hierarchy-terminology).

## Yandex Readers

#### Source API

[Yandex Direct API](https://tech.yandex.com/direct/)

#### How to obtain credentials

In order to access Yandex Direct API, you need two accounts: an advertiser account and a developer account.
Here is the process:

1. Create a developer account if you don't already have one. Click on the *Get started* button on this [page](https://direct.yandex.com/).
2. Create and register an app that will access Yandex Direct API via [Yandex OAuth](https://oauth.yandex.com/client/new).
3. Keep app client id safe. Log in with your advertiser account and [give permission to the app to access your data](https://tech.yandex.com/oauth/doc/dg/tasks/get-oauth-token-docpage/).
4. Store your token very carefully.
5. Log out and log in as a developer and [ask permission to access Yandex Direct API](https://direct.yandex.com/registered/main.pl?cmd=apiSettings) (ask for Full access). Fill in the form.
6. Wait for Yandex support to reply but it should be within a week.

### Yandex Campaign Reader

[Official documentation](https://tech.yandex.com/direct/doc/ref-v5/campaigns/get-docpage/)

#### Quickstart

The following command retrieves the daily budget of all your campaigns, since your account creation.

```
python nck/entrypoint.py read_yandex_campaigns --yandex-token <TOKEN> --yandex-field-name Id --yandex-field-name Name --yandex-field-name DailyBudget write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

|CLI option|Documentation|
|--| -|
|`--yandex-token`|Bear token that allows you to authenticate to the API|
|`--yandex-campaign-id`|(Optional) Selects campaigns with the specified IDs.|
|`--yandex-campaign-state`|(Optional) Selects campaigns with the specified states. *Possible values can be found [here](https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status).*|
|`--yandex-campaign-status`|(Optional) Selects campaigns with the specified statuses. *Possible values can be found [here](https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status).*|
|`--yandex-campaign-payment-status`|(Optional) Selects campaigns with the specified payment [statuses](https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status).|
|`--yandex-field-name`|Parameters to get that are common to all types of campaigns.|

### Yandex Statistics Reader

[Official documentation](https://tech.yandex.com/direct/doc/reports/reports-docpage/)

#### Quickstart

The following command retrieves a performance report for all your campaigns, since your account creation.

```
python nck/entrypoint.py read_yandex_statistics --yandex-token <TOKEN> --yandex-report-type AD_PERFORMANCE_REPORT --yandex-field-name AdFormat --yandex-field-name AdId --yandex-field-name Impressions --yandex-include-vat True --yandex-report-language en --yandex-field-name AdGroupName --yandex-field-name AdGroupId --yandex-field-name AdNetworkType --yandex-field-name CampaignId --yandex-field-name CampaignName --yandex-field-name CampaignType --yandex-field-name Date --yandex-field-name Device --yandex-field-name Clicks --yandex-field-name Conversions --yandex-field-name Cost --yandex-date-range ALL_TIME write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

Detailed version [here](https://tech.yandex.com/direct/doc/reports/spec-docpage/).

|CLI option|Documentation|
|--|--|
|`--yandex-token`|Bear token that allows you to authenticate to the API|
|`--yandex-report-language`|(Optional) Language of the report. *Possible values can be found [here](https://tech.yandex.com/direct/doc/dg/concepts/headers-docpage/#headers__accept-language).*|
|`--yandex-filter`|(Optional) Filters on a particular field.|
|`--yandex-max-rows`|(Optional) The maximum number of rows in the report.|
|`--yandex-field-name`|Information you want to collect. *Possible values can be found [here](https://tech.yandex.com/direct/doc/reports/fields-list-docpage/).*|
|`--yandex-report-type`|Type of report. Linked to the fields you want to select.|
|`--yandex-date-range`|*Possible values can be found [here](https://tech.yandex.com/direct/doc/reports/period-docpage/).*|
|`--yandex-include-vat`|Adds VAT to your expenses if set to `True`|
|`--yandex-date-start`|(Optional) Selects data on a specific period of time. Combined with `--yandex-date-stop` and  `--yandex-date-range` set to `CUSTOM_DATE`.|
|`--yandex-date-stop`|(Optional) Selects data on a specific period of time. Combined with `--yandex-date-start` and  `--yandex-date-range` set to `CUSTOM_DATE`.|

## Troubleshooting

You encountered an issue when running a Reader command and you don't know what's going on?
You may find an answer in the troubleshooting guide below.

1. **Have you installed NCK dependencies?** In order to run NCK, you need to install all dependencies. First create a [virtual environment](https://docs.python.org/3/library/venv.html) and then run `pip install -r requirements.txt`.
2. **Have you set `PYTHONPATH` environment variable to the root of NCK folder?**
3. **Have you checked logs?** The code has been implemented so that every error is logged. For example, if you did not provide a valid token, you will see something like ```Invalid request.
{'error': {'error_code': '53', 'request_id': '8998435864716615689', 'error_string': 'Authorization error', 'error_detail': 'Invalid OAuth token'}}```. If you misspelled a field, you will get a message like this one: ```Error: Invalid value for "--yandex-field-name"```.
