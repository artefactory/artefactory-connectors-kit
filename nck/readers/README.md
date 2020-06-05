# NCK Readers

Each reader role is to read data from external source and transform it into a Stream understable format to be written on GCS and BQ thanks to the corresponding writers.

## Step to create a new Reader

1. Create python module following naming nomenclature ``` [command]_reader.py ```
2. Implement `read` method
3. Create click command with required options
4. Reference click command into [commands list](./__init__.py)
5. Update current README.md

## Facebook Reader

#### Quickstart

The Facebook Reader handles calls to 2 endpoints of the Facebook Marketing API: **Facebook Ad Insights** (to retrieve performance data), and **Facebook Object Node** (to retrieve configuration data).

*Example of Facebook Ad Insights Request*
```
python nck/entrypoint.py read_facebook --facebook-access-token <ACCESS_TOKEN> --facebook-object-id <OBJECT_ID> --facebook-breakdown age --facebook-breakdown gender --facebook-action-breakdown action_type --facebook-field ad_id --facebook-field ad_name --facebook-field impressions --facebook-field clicks --facebook-field actions[action_type:post_engagement] --facebook-field actions[action_type:video_view] --facebook-field age --facebook-field gender --facebook-time-increment 1 --facebook-start-date 2020-01-01 --facebook-end-date 2020-01-03 write_console
```

*Example of Facebook Object Node Request*
```
python nck/entrypoint.py read_facebook --facebook-access-token <ACCESS_TOKEN> --facebook-object-id <OBJECT_ID>  --facebook-ad-insights False --facebook-level ad --facebook-field id --facebook-field creative[id] --facebook-add-date-to-report True --facebook-start-date 2020-01-01 --facebook-end-date 2019-01-01 write_console
```

#### Parameters

|CLI option|Documentation|
|:--|:--|
|`--facebook-app-id`|Facebook App ID. *Not mandatory if Facebook Access Token is provided.*|
|`--facebook-app-secret`|Facebook App Secret. *Not mandatory if Facebook Access Token is provided.*|
|`--facebook-access-token`|Facebook App Access Token.|
|`--facebook-object-type`|Nature of the root Facebook Object used to make the request. *Supported values: creative (available only for Facebook Object Node requests), ad, adset, campaign, account (default).*|
|`--facebook-object-id`|ID of the root Facebook Object used to make the request.|
|`--facebook-level`|Granularity of the response. *Supported values: creative (available only for Facebook Object Node requests), ad (default), adset, campaign or account.*|
|`--facebook-ad-insights`|*True* (default) if *Facebook Ad Insights* request, *False* if *Facebook Object Node* request.|
|`--facebook-field`|Fields to be retrieved.|
|`--facebook-start-date`|Start date of the requested time range. *This parameter is only relevant for Facebook Ad Insights Requests, and Facebook Object Node requests at the Campaign, Adset and Ad levels.*|
|`--facebook-end-date`|End date of the requested time range. *This parameter is only relevant for Facebook Ad Insights Requests, and Facebook Object Node requests at the Campaign, Adset and Ad levels.*|
|`--facebook-date-preset`|Relative time range. Ignored if *--facebook-start date* and *--facebook-end-date* are specified. *This parameter is only relevant for Facebook Ad Insights Requests, and Facebook Object Node requests at the Campaign, Adset and Ad levels.*|
|`--facebook-time-increment`|Cuts the results between smaller time slices within the specified time range. *This parameter is only relevant for Facebook Ad Insights Requests, and Facebook Object Node requests at the Campaign, Adset and Ad levels.*|
|`--facebook-add-date-to-report`|*True* if you wish to add the date of the request to each response record, *False* otherwise (default).|
|`--facebook-breakdown`|How to break down the result. *This parameter is only relevant for Facebook Ad Insights Requests.*|
|`--facebook-action-breakdown`|How to break down action results. *This parameter is only relevant for Facebook Ad Insights Requests.*|

#### Additional details for a relevant use of the Facebook Reader

**#1: Make sure to select the appropriate `--facebook-level`**

|If Facebook Object Type is...|Facebook Level can be...|
|:--|:--|
|`account`|account, campaign, adset, ad, creative|
|`campaign`|campaign, adset, ad|
|`adset`|adset, ad, creative|
|`ad`|ad, creative|
|`creative`|creative|

**#2: Format Facebook Reader response using `--facebook-fields`**

2.1. The list of **applicable fields** can be found on the links below:

- **Facebook Ad Insights Request**: [all fields](https://developers.facebook.com/docs/marketing-api/insights/parameters/v7.0)
- **Facebook Object Node Request**: [Account-level fields](https://developers.facebook.com/docs/marketing-api/reference/ad-account), [Campaign-level fields](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group), [Adset-level fields](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign), [Ad-level fields](https://developers.facebook.com/docs/marketing-api/reference/adgroup), [Creative-level fields](https://developers.facebook.com/docs/marketing-api/reference/ad-creative)

2.2. If you want to select **a nested field value**,  simply indicate the path to this value within the request field.

*Facebook Reader Request*
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

*Facebook Reader Response*
```
{"object_story_spec_video_data_call_to_action_value_link": "https://www.artefact.com"}
```

(2.3) **Action Breakdown filters** can be applied to the fields of ***Facebook Ad Insights* Requests** using the following syntax: <FIELD_NAME>[<ACTION_BREAKDOWN>:<ACTION_BREAKDOWN_VALUE>]. You can combine multiple Action Breakdown filters on the same field by adding them in cascade next to each other.

*Facebook Reader Request*
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
*Facebook Reader Response*
```
{"actions_action_type_video_view": "17", "actions_action_type_post_engagement": "25"}
```

## Twitter Ads Reader

#### How to obtain credentials

* **Apply for a developper account** trough [this link](https://developer.twitter.com/en/apply).
* **Create a Twitter app** on the developper portal: it will generate your authentication credentials.
* **Apply for Twitter Ads API access** by filling out [this form]([https://developer.twitter.com/en/docs/ads/general/overview/adsapi-application](https://developer.twitter.com/en/docs/ads/general/overview/adsapi-application)). Receiving Twitter approval may take up to 7 business days.
* **Get a Campaign Analyst access to the Twitter Ads account** you wish to retrieve data for, on the @handle that you used to create your Twitter App.

#### Quickstart

The Twitter Ads Reader can collect **3 types of reports**, making calls to 3 endpoints of the Twitter Ads API:
* **ANALYTICS reports**, making calls to the [Asynchronous Analytics endpoint](https://developer.twitter.com/en/docs/ads/analytics/api-reference/asynchronous). These reports return performance data for a wide range of metrics, that **can be aggregated over time**. Output data **can be splitted by day** when requested over a larger time period.
* **REACH reports**, making calls to the [Reach and Average Frequency endpoint](https://developer.twitter.com/en/docs/ads/analytics/api-reference/reach). These reports return performance data with a focus on reach and frequency metrics, that **cannot be aggregated over time** (*e.g. the reach of day A and B is not equal to the reach of day A + the reach of day B, as it counts unique individuals*). Output data **cannot be splitted by day** when requested over a larger time period. These reports are available **only for the Funding Instrument and Campaign entities**.
* **ENTITY reports**, making calls to [Campaign Management endpoints](https://developer.twitter.com/en/docs/ads/campaign-management/api-reference). These reports return details on entity configuration since the creation of the Twitter Ads account.

*Call example for ANALYTICS reports*
This call will collect engagement metrics for Line Item entities, splitting the results by day, from 2020-01-01 to 2020-01-03:
```
python nck/entrypoint.py read_twitter --twitter-consumer-key <API_KEY> --twitter-consumer-secret <API_SECRET_KEY> --twitter-access-token <ACCESS_TOKEN> --twitter-access-token-secret <ACCESS_TOKEN_SECRET> --twitter-account-id <ACCOUNT_ID> --twitter-report-type ANALYTICS --twitter-entity LINE_ITEM --twitter-metric-group ENGAGEMENT --twitter-segmentation-type AGE --twitter-granularity DAY --twitter-start-date 2020-01-01 --twitter-end-date 2020-01-03 write_console
```

*Call example for REACH reports*
This call will collect reach metrics (*total_audience_reach, average_frequency*) for Campaign entities, from 2020-01-01 to 2020-01-03:
```
python nck/entrypoint.py read_twitter --twitter-consumer-key <API_KEY> --twitter-consumer-secret <API_SECRET_KEY> --twitter-access-token <ACCESS_TOKEN> --twitter-access-token-secret <ACCESS_TOKEN_SECRET> --twitter-account-id <ACCOUNT_ID> --twitter-report-type REACH --twitter-entity CAMPAIGN --twitter-start-date 2020-01-01 --twitter-end-date 2020-01-03 write_console
```

*Call example for ENTITY reports*
This call collects details on the configuration of Campaign entities (id, name, total_budget_amount_local_micro, currency), since the creation of the Twitter Ads account:
```
python nck/entrypoint.py read_twitter --twitter-consumer-key <API_KEY> --twitter-consumer-secret <API_SECRET_KEY> --twitter-access-token <ACCESS_TOKEN> --twitter-access-token-secret <ACCESS_TOKEN_SECRET> --twitter-account-id <ACCOUNT_ID> --twitter-report-type REACH --twitter-entity CAMPAIGN --twitter-entity-attribute id --twitter-entity-attribute name --twitter-entity-attribute total_budget_amount_local_micro --twitter-entity-attribute currency write_console
```

#### Parameters

|CLI option|Documentation|
|--|--|
|`--twitter-consumer-key`|API key, available in the 'Keys and tokens' section of your Twitter Developper App.|
|`--twitter-consumer-secret`|API secret key, available in the 'Keys and tokens' section of your Twitter Developper App.|
|`--twitter-access-token`|Access token, available in the 'Keys and tokens' section of your Twitter Developper App.|
|`--twitter-access-token-secret`|Access token secret, available in the 'Keys and tokens' section of your Twitter Developper App.|
|`--twitter-account-id`|Specifies the Twitter Account ID for which the data should be returned.|
|`--twitter-report-type`|Specifies the type of report to collect. *Possible values: ANALYTICS, REACH, ENTITY.*|
|`--twitter-entity`|Specifies the entity type to retrieve data for. *Possible values: FUNDING_INSTRUMENT, CAMPAIGN, LINE_ITEM, MEDIA_CREATIVE, PROMOTED_TWEET.*|
|`--twitter-entity-attribute`|Specific to ENTITY reports. Specifies the entity attribute (configuration detail) that should be returned.|
|`--twitter-granularity`|Specific to ANALYTICS reports. Specifies how granular the retrieved data should be. *Possible values: TOTAL (default), DAY.*|
|`--twitter-metric-group`|Specific to ANALYTICS reports. Specifies the list of metrics (as a group) that should be returned. *Possible values can be found [here](https://developer.twitter.com/en/docs/ads/analytics/overview/metrics-and-segmentation).* |
|`--twitter-placement`|Specific to ANALYTICS reports. Scopes the retrieved data to a particular placement. *Possible values: ALL_ON_TWITTER (default), PUBLISHER_NETWORK.*|
|`--twitter-segmentation-type`|Specific to ANALYTICS reports. Specifies how the retrieved data should be segmented. *Possible values can be found [here](https://developer.twitter.com/en/docs/ads/analytics/overview/metrics-and-segmentation).* |
|`--twitter-platform`|Specific to ANALYTICS reports. Required if segmentation_type is set to DEVICES or PLATFORM_VERSION. *Possible values can be identified through the targeting_criteria/locations*|
|`--twitter-country`|Specific to ANALYTICS reports. Required if segmentation_type is set to CITIES, POSTAL_CODES, or REGION. *Possible values can be identified through the GET targeting_criteria/platforms endpoint.*|
|`--twitter-start-date`|Specifies report start date (format: YYYY-MM-DD).|
|`--twitter-end-date`|Specifies report end date (format: YYYY-MM-DD).|
|`--twitter-add-request-date-to-report`|If set to *True* (default: *False*), the date on which the request is made will appear on each report record.|

If you need any further information, the documentation of Twitter Ads API can be found [here](https://developer.twitter.com/en/docs/ads/general/overview).

## Google Readers

### Authentication

You can authenticate to most of the readers of the google 
suite following the same schema. You'll need to generate a **refresh token** to connect
via the oAuth flow. A full script to do this can be found here:

[Refresh token generator](https://github.com/artefactory/Refresh-token-generator-for-google-oauth)


### Google Ads Reader

#### How to obtain Credentials


Using the Google Ads API requires four things:
- A developer token (Generated at a company level - one per company -, takes around 2 days to be approved by Google) which can be completely independant from the Google Ads Account you will be calling (though you need a Manager Google Ads Account to request a token for your company)

- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>

- A refresh token, created with the email address able to access to all the Google Ads Account you will be calling

- The ID of the GAds Accounts <CLIENT_CUSTOMER_ID> you will be reading from (XXX-XXX-XXXX numbers, written right next to your Account Name)

See the [documentation here](https://developers.google.com/adwords/api/docs/guides/signup "Sign Up for Google Ads API")
to apply for access if your Company does not already have a developer token (granting you the right to use the API).

See the [documentation here](https://developers.google.com/adwords/api/docs/guides/first-api-call "Make your first API call")
to set-up your OAuth2 credentials and refresh token specifically for your Google Ads Accounts.


#### Which Reports and Metrics are available in the API

The list of available reports for the API, and the associated metrics, can be [found here](https://developers.google.com/adwords/api/docs/appendix/reports#available-reports "Report Types")

#### Simple API call example

- Call Example


The following command retrieves insights about the Ads of *my_first_campaign* and *my_second_campaign* in the Google Ads Account <CLIENT_CUSTOMER_ID> thanks to
your company <DEVELOPER_TOKEN>, and your <CLIENT_ID>, <CLIENT_SECRET> and <REFRESH_TOKEN> with the necessary permissions to access your Accounts.

```
python nck/entrypoint.py read_googleads --googleads-developer-token <DEVELOPER_TOKEN> --googleads-client-id <CLIENT_ID> --googleads-client-secret <CLIENT_SECRET> --googleads-refresh-token <REFRESH_TOKEN> --googleads-client-customer-id <XXX-XXX-XXXX CLIENT_CUSTOMER_ID> --googleads-report-type AD_PERFORMANCE_REPORT --googleads-date-range-type LAST_7_DAYS --googleads-field CampaignName --googleads-field AdGroupName --googleads-field Headline --googleads-field Date --googleads-field Impressions --googleads-report-filter "{'field':'CampaignName','operator':'IN','values':['my_first_campaign','my_second_campaign']}" 
```

*If it doesn't work, try to* `export PYTHONPATH="."` *in the nautilus-connector-kit folder (to be sure Python is reading correctly)*
*If you want the output to be printed in your console, add* `write_console` *at the end of your command (see writers for more details)*

- Parameters of the GoogleAds Readers


| --googleads-developer-token | --googleads-client-id | --googleads-client-secret | --googleads-refresh-token | --googleads-manager-id | --googleads-client-customer-id  | --googleads-report-name | --googleads-report-type | --googleads-date-range-type | --googleads-start-date | --googleads-end-date | --googleads-field | --googleads-report-filter | --googleads-include-zero-impressions | --googleads-filter-on-video-campaigns | --googleads-include-client-customer-id |
|:-----------------:|:---------------------:|:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:|:--------------------:|:---------------------------:|:----------------------:|:-------------------:|:-------------------------:|:----------------:|:------------------------:|:------------------------:|:------------------------:|:------------------------:|
|Company Developer token for Google Ads API |OAuth2 ID| OAuth2 Secret|Refresh token for OAuth2|Manager_Account_ID (XXX-XXX-XXXX identifier) (optional)|GAds_Account_ID (ignored if a manager account ID was given)|Optional Name for your output stream ("Custom Report" by default)|Type of Report to be called|Type of Date Range to apply (if "CUSTOM_RANGE", a min and max date must be specified) |Start Date for "CUSTOM_RANGE" date range (optional)|End Date for "CUSTOM_RANGE" date range (optional)|List of fields to request |Filter to apply on a chosen field (Dictionary as String "{'field':,'operator':,'values':}")|Boolean specifying whether or not rows with zero impressions should be included in report| Boolean used to filter on Video Campaigns only (require CampaignId to be listed as a field) | Boolean used to add "AccountId" as a field in the output stream * |

\* *AccountId is not available in the API but is known since it's a requirement to call the API (= client customer ID)*

See the documents below for a better understanding of the parameters:
- [Google Ads API Reporting Basics](https://developers.google.com/adwords/api/docs/guides/reporting#create_a_report_definition)
- [Possible Date Ranges](https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges)


### Google Search Console Reader

#### How to obtain Credentials

Using the Google Search Console API requires three main parameters:
- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>

- A refresh token, created with the email address able to access to your Google Search Console Account.

- The URLs whose performance you want to see.

See the [documentation here](https://developers.google.com/webmaster-tools/search-console-api-original/v3/prereqs "Search Console API")
to see an Overview of the Search Console API.


#### Search Analytics

The list of available dimensions and metrics in the API can be [found here](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query "Search Analytics")

#### Simple API call example

- Call Example

The following command retrieves insights about the URL <SITE_URL> thanks to your company <CLIENT_ID> and <REFRESH_TOKEN> 
with the necessary permissions to access your Accounts.

```
python nck/entrypoint.py read_search_console --search-console-client-id <CLIENT_ID> --search-console-refresh-token <REFRESH_TOKEN> --search-console-site-url <SITE_URL> --search-console-dimensions country --search-console-dimensions device --search-console-start-date 2020-01-01 --search-console-end-date 2020-01-01 write_console 
```

- Parameters of the Google Search Console Readers

| --search-console-client-id | --search-console-client-secret | --search-console-access-token | --search-console-refresh-token | --search-console-dimensions | --search-console-site-url  | --search-console-start-date | --search-console-end-date | --search-console-date-column | --search-console-row-limit |
|:-----------------:|:---------------------:|:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:|:--------------------:|:---------------------------:|:----------------------:|:----------------------:|
|OAuth2 ID| OAuth2 Secret| Access token | Refresh token for OAuth2 | [Dimensions to request](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query#dimensionFilterGroups.filters.dimension) |Site URL whose performance you want to request| Start Date for the request | End Date for the request | If true, include date column in the report | Row number by report page |

See the documents below for a better understanding of the parameters:
- [Google Search Console API](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)


### Search Ads 360 Reader (SA360)

#### How to obtain Credentials

Using the Search Ads API requires two things:

- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>

- A refresh token, created with the email address able to access to all the Search Ads 360 Account you will be calling

See the [documentation here](https://developers.google.com/search-ads/v2/authorizing "SA360 Authentication")
to set-up your OAuth2 credentials and refresh token specifically for Search Ads 360 Reporting.


#### Which Reports and Metrics are available in the API

The list of available reports for the API, and the associated metrics, can be [found here](https://developers.google.com/search-ads/v2/report-types "Report Types")

#### Simple API call example

- Call Example


The following command retrieves insights about the Ads in the Search Ads 360 Account <ADVERTISER_ID> from the agency <AGENCY_ID> thanks to
your <CLIENT_ID>, <CLIENT_SECRET> and <REFRESH_TOKEN> with the necessary permissions to access your Accounts.

```
python nck/entrypoint.py read_sa360 --sa360-client-id <CLIENT_ID> --sa360-client-secret <CLIENT_SECRET> --sa360-refresh-token <REFRESH_TOKEN> --sa360-agency-id <AGENCY_ID> --sa360-advertiser-id <ADVERTISER_ID> --sa360-report-type keyword --sa360-column date --sa360-column impr --sa360-column clicks --sa360-start-date 2020-01-01 --sa360-end-date 2020-01-01 
```

*If it doesn't work, try to* `export PYTHONPATH="."` *in the nautilus-connector-kit folder (to be sure Python is reading correctly)*
*If you want the output to be printed in your console, add* `write_console` *at the end of your command (see writers for more details)*


- Parameters of the SA360 Reader

| CLI option | Documentation |
| ---------- | ------------- |
|`--sa360-access-token` | (Optional) Access token |
|`--sa360-client-id` | OAuth2 ID |
|`--sa360-client-secret` | OAuth2 ID Secret |
|`--sa360-refresh-token` | Refresh token |
|`--sa360-agency-id` | Agency ID to request in SA360 |
|`--sa360-advertiser-id` | (Optional) Advertiser ids to request. If not provided, every advertiser of the agency will be requested|
|`--sa360-report-name` | (Optional) Name of the output report |
|`--sa360-report-type` | Type of the report to request. List [here](https://developers.google.com/search-ads/v2/report-types)|
|`--sa360-column` | Dimensions and metrics to request in the report |
|`--sa360-saved-column` | (Optional) Saved columns to report. See [documentation](https://developers.google.com/search-ads/v2/how-tos/reporting/saved-columns)|
|`--sa360-start-date` | Start date of the period to request |
|`--sa360-end-date` | End date of the period to request |

See the documents below for a better understanding of the parameters:
- [SA360 Reporting](https://developers.google.com/search-ads/v2/how-tos/reporting)


## Yandex readers

For now, there is only one Yandex API you can access through Nautilus connectors: [Direct API](https://tech.yandex.com/direct/).
This API allows you to collect display metrics.

### Access Yandex Direct API

In order to access Yandex Direct API, you need two accounts: an advertiser account and a developer account.
Here is the process:

1. Create a developer account if you don't already have one. Click on the *Get started* button on this [page](https://direct.yandex.com/).
2. Create and register an app that will access Yandex Direct API via [Yandex OAuth](https://oauth.yandex.com/client/new).
3. Keep app client id safe. Log in with your advertiser account and [give permission to the app to access your data](https://tech.yandex.com/oauth/doc/dg/tasks/get-oauth-token-docpage/).
4. Store your token very carefully.
5. Log out and log in as a developer and [ask permission to access Yandex Direct API](https://direct.yandex.com/registered/main.pl?cmd=apiSettings) (ask for Full access). Fill in the form.
6. Wait for Yandex support to reply but it should be within a week.

### Yandex campaign reader

[Official documentation](https://tech.yandex.com/direct/doc/ref-v5/campaigns/get-docpage/)

#### Quickstart

If you want to quickly get to the point, here is a simple command that get the daily budget for all your campaigns.

```bash
python nck/entrypoint.py read_yandex_campaigns --yandex-token <TOKEN> --yandex-field-name Id --yandex-field-name Name --yandex-field-name DailyBudget write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

| CLI option | Documentation |
| ---------- | ------------- |
| `--yandex-token` | Bear token that allows you to authenticate to the API |
| `--yandex-campaign-id` | (Optional) Selects campaigns with the specified IDs. |
| `--yandex-campaign-state` | (Optional) Selects campaigns with the specified [states](https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status). |
| `--yandex-campaign-status` | (Optional) Selects campaigns with the specified [statuses](https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status). |
| `--yandex-campaign-payment-status` | (Optional) Selects campaigns with the specified payment [statuses](https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status). |
| `--yandex-field-name` | Parameters to get that are common to all types of campaigns. |

### Yandex statistics reader

[Official documentation](https://tech.yandex.com/direct/doc/reports/reports-docpage/)

#### Quickstart

The command below gives you a performance report for all your campaigns and since the beginning.

```bash
python nck/entrypoint.py read_yandex_statistics --yandex-token <TOKEN> --yandex-report-type AD_PERFORMANCE_REPORT --yandex-field-name AdFormat --yandex-field-name AdId --yandex-field-name Impressions --yandex-include-vat True --yandex-report-language en --yandex-field-name AdGroupName --yandex-field-name AdGroupId --yandex-field-name AdNetworkType --yandex-field-name CampaignId --yandex-field-name CampaignName --yandex-field-name CampaignType --yandex-field-name Date --yandex-field-name Device --yandex-field-name Clicks --yandex-field-name Conversions --yandex-field-name Cost --yandex-date-range ALL_TIME write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

Detailed version [here](https://tech.yandex.com/direct/doc/reports/spec-docpage/).

| CLI option | Documentation |
| ---------- | ------------- |
| `--yandex-token` | Bear token that allows you to authenticate to the API |
| `--yandex-report-language` | (Optional) Language of the report. See all options [here](https://tech.yandex.com/direct/doc/dg/concepts/headers-docpage/#headers__accept-language). |
| `--yandex-filter` | (Optional) Filters on a particular field. |
| `--yandex-max-rows` | (Optional) The maximum number of rows in the report. |
| `--yandex-field-name` | Information you want to collect. Complete list [here](https://tech.yandex.com/direct/doc/reports/fields-list-docpage/). |
| `--yandex-report-type` | Type of report. Linked to the fields you want to select. |
| `--yandex-date-range` | List [here](https://tech.yandex.com/direct/doc/reports/period-docpage/). |
| `--yandex-include-vat` | Adds VAT to your expenses if set to `True`|
| `--yandex-date-start` | (Optional) Selects data on a specific period of time. Combined with `--yandex-date-stop` and  `--yandex-date-range` set to `CUSTOM_DATE`. |
| `--yandex-date-stop` | (Optional) Selects data on a specific period of time. Combined with `--yandex-date-start` and  `--yandex-date-range` set to `CUSTOM_DATE`. |

## Adobe Analytics Readers

As of May 2020 (last update of this section of the documentation), **two versions of Adobe Analytics Reporting API are  coexisting: 1.4 and 2.0**. As some functionalities of API 1.4 have not been made available in API 2.0 yet (Data Warehouse reports in particular), our Adobe Analytics Readers are also available in these two versions.

### Adobe Analytics Reader 1.4

#### How to obtain credentials

Our Adobe Analytics Reader 1.4 uses the **WSSE authentication framework**. This authentication framework is now deprecated, so you won't be able to generate new WSSE authentication credentials (Username, Password) on Adobe Developper Console if you don't already have them.

#### Quickstart

Call example to Adobe Analytics Reader 1.4, getting the number of visits per day and tracking code for a specified Report Suite, between 2020-01-01 and 2020-01-31:

```
python nck/entrypoint.py read_adobe --adobe-username <USERNAME>  --adobe-password <PASSWORD> --adobe-report-suite-id <REPORT_SUITE_ID> --adobe-date-granularity day --adobe-report-element-id trackingcode --adobe-report-metric-id visits --adobe-start-date 2020-01-01 --adobe-end-date 2020-01-31 write_console
```

#### Parameters

|CLI option|Documentation|
|--|--|
|`--adobe-username`|Username used for WSSE authentication|
|`--adobe-password`|Password used for WSSE authentication|
|`--adobe-list-report-suite`|Should be set to *True* if you wish to request the list of available Adobe Report Suites (*default: False*). If set to *True*, the below parameters should be left empty.|
|`--adobe-report-suite-id`|ID of the requested Adobe Report Suite|
|`--adobe-report-element-id`|ID of the element (i.e. dimension) to include in the report|
|`--adobe-report-metric-id`|ID of the metric to include in the report|
|`--adobe-date-granularity`|Granularity of the report. *Possible values: PREVIOUS_DAY, LAST_30_DAYS, LAST_7_DAYS, LAST_90_DAYS*|
|`--adobe-start-date`|Start date of the report (format: YYYY-MM-DD)|
|`--adobe-end-date`|End date of the report (format: YYYY-MM-DD)|

#### Addtional information
- **The full list of available elements and metrics** can be retrieved with the [GetElements](https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/reporting-api/methods/r_GetElements.md) and [GetMetrics](https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/reporting-api/methods/r_GetMetrics.md) methods.
- **Adobe Analytics Reader 1.4 requests Data Warehouse reports** (the "source" parameter is set to "warehouse" in the report description), allowing it to efficiently process multiple-dimension requests.
- **If you need further information**, the documentation of Adobe APIs 1.4 can be found [here](https://github.com/AdobeDocs/analytics-1.4-apis).

### Adobe Analytics Reader 2.0

#### How to obtain credentials

Adobe Analytics Reader 2.0 uses the **JWT authentication framework**.
- Get developper access to Adobe Analytics (documentation can be found [here](https://helpx.adobe.com/enterprise/using/manage-developers.html))
- Create a Service Account integration to Adobe Analytics on [Adobe Developper Console](https://console.adobe.io/)
- Use the generated JWT credentials (Client ID, Client Secret, Technical Account ID, Organization ID and private.key file) to retrieve your Global Company ID (to be requested to [Discovery API](https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/discovery.md')). All these parameters will be passed to Adobe Analytics Reader 2.0.

#### Quickstart

Call example to Adobe Analytics Reader 2.0, getting the number of visits per day and tracking code for a specified Report Suite, between 2020-01-01 and 2020-01-31:

```
python nck/entrypoint.py read_adobe_2_0 --adobe-client-id <CLIENT_ID> --adobe-client-secret <CLIENT_SECRET> --adobe-tech-account-id <TECH_ACCOUNT_ID> --adobe-org-id <ORG_ID> --adobe-private-key <PRIVATE_KEY> --adobe-global-company-id <GLOBAL_COMPANY_ID> --adobe-report-suite-id <REPORT_SUITE_ID> --adobe-dimension daterangeday --adobe-dimension campaign --adobe-start-date 2020-01-01 --adobe-end-date 2020-01-31 --adobe-metric visits write_console
```

#### Parameters

|CLI option|Documentation|
|--|--|
|`--adobe-client-id`|Client ID, that you can find on Adobe Developper Console|
|`--adobe-client-secret`|Client Secret, that you can find on Adobe Developper Console|
|`--adobe-tech-account-id`|Technical Account ID, that you can find on Adobe Developper Console|
|`--adobe-org-id`|Organization ID, that you can find on Adobe Developper Console|
|`--adobe-private-key`|Content of the private.key file, that you had to provide to create the integration. Make sure to enter the parameter in quotes, include headers, and indicate newlines as \n.|
|`--adobe-global-company-id`|Global Company ID (to be requested to [Discovery API](https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/discovery.md'))|
|`--adobe-report-suite-id`|ID of the requested Adobe Report Suite|
|`--adobe-dimension`|Dimension to include in the report|
|`--adobe-metric`|Metric  to include in the report|
|`--adobe-start-date`|Start date of the report (format: YYYY-MM-DD)|
|`--adobe-end-date`|End date of the report (format: YYYY-MM-DD)|

#### Additional information

- **In API 2.0, dimension and metric names are slightly different from API 1.4**. To get new metric and dimension names and reproduce the behavior of Adobe Analytics UI as closely as possible,  [enable the Debugger feature in Adobe Analytics Workspace](https://github.com/AdobeDocs/analytics-2.0-apis/blob/master/reporting-tricks.md): it allow you to visualize the back-end JSON requests made by Adobe Analytics UI to Reporting API 2.0.
-  **In API 2.0, the date granularity parameter was removed, and should now be handled as a dimension**: a request featuring `--adobe-dimension daterangeday` will produce a report with a day granularity.
- **API 2.0 does not feature Data Warehouse reports yet** (along with other features, that are indicated on the "Current limitations" section of [this page](https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/migration-guide.md)). For this reason, if you wish to collect multiple-dimension reports, Adobe Analytics Reader 1.4 might be a more efficient solution in terms of processing time. 
- **If you need any further information**, the documentation of Adobe APIs 2.0 can be found [here](https://github.com/AdobeDocs/analytics-2.0-apis).

### Troubleshooting

You encountered and you don't know what 's going on. You may find an answer in the troubleshooting guide below.

1. **Have you install NCK dependencies?** In order to run NCK, you need to install all dependencies. First create a [virtual environment](https://docs.python.org/3/library/venv.html) and then run `pip install -r requirements.txt`.
2. **Have you set `PYTHONPATH` environment variable to the root of NCK folder?**
3. **Have you checked logs?** The code has been implmented so that every error is logged. For example, if you did not provide a valid token, you will see something like ```Invalid request.
{'error': {'error_code': '53', 'request_id': '8998435864716615689', 'error_string': 'Authorization error', 'error_detail': 'Invalid OAuth token'}}```. If you misspelled a field, you will get a message like this one: ```Error: Invalid value for "--yandex-field-name"```.
