# NCK Readers

Each reader role is to read data from external source and transform it into a Stream understable format to be written on GCS and BQ thanks to the corresponding writers.

## Step to create a new Reader

1. Create python module following naming nomenclature ``` [command]_reader.py ```
2. Implement `read` method
3. Create click command with required options
4. Reference click command into [commands list](./__init__.py)
5. Update current README.md


## Facebook Reader

- Example

The following command retrieves some insights of every Ads in the Facebook account <ACCOUNT_ID> thanks to
a Facebook App whose access_token is <ACCESS_TOKEN>.

```
python nck/entrypoint.py read_facebook --facebook-access-token <ACCESS_TOKEN> --facebook-ad-object-id <ACCOUNT_ID> --facebook-breakdown gender --facebook-ad-level ad --facebook-start-date 2019-01-01 --facebook-end-date 2019-01-01 --facebook-field date_start --facebook-field date_stop --facebook-field account_currency --facebook-field account_id --facebook-field account_name --facebook-field ad_id --facebook-field ad_name --facebook-field adset_id --facebook-field adset_name --facebook-field campaign_id --facebook-field campaign_name --facebook-field clicks --facebook-field impressions --facebook-desired-field date_start --facebook-desired-field date_stop --facebook-desired-field account_name --facebook-desired-field account_id --facebook-desired-field ad_id --facebook-desired-field ad_namefacebook-desired-field clicks --facebook-desired-field impressions write_console
```

The report below is the output of the command. You can easily store it in GCS or Biquery thanks to the corresponding
writers([GCS writer](../writers/gcs_writer.py), [BQ writer](../writers/bigquery_writer.py)):
```
{
  "date_start": "2019-01-05",
  "date_stop": "2019-01-05",
  "account_name": "example_name"
  "account_id": "0000000000"
  "ad_id": "00000000000",
  "ad_name": "example_name",
  "clicks": "1",
  "impressions": "100"
}
```
See the [documentation here](https://developers.facebook.com/docs/marketing-api/insights/#marketing-api-quickstart "Create a Facebook App")
to create a Facebook App and an access token.

- Parameters of the Facebook Readers

| --facebook-app-id | --facebook-app-secret | --facebook-access-token | --facebook-ad-object-id | --facebook-ad-object-type | --facebook-breakdown | --facebook-action-breakdown | --facebook-ad-insights | --facebook-ad-level | --facebook-time-increment | --facebook-field | --facebook-desired-field | --facebook-start-date | --facebook-end-date | --facebook-date-preset | --facebook-recurse-level |
|:-----------------:|:---------------------:|:-----------------------:|:-----------------------:|:-------------------------:|:--------------------:|:---------------------------:|:----------------------:|:-------------------:|:-------------------------:|:----------------:|:------------------------:|:---------------------:|:-------------------:|:----------------------:|:------------------------:|
|Facebook App ID |Facebook App ID| Facebook App access token|Object ID to request (account ID, campaign ID, ...)|Object type (account, campaign, ...)|List of breakdowns for the request|List of action-breakdowns for the request|Request insights or not |Level of request|Time increment|List of fields to request|Desired fields in the output report |Start date of period|End date of period| Preset period|Allows to go down in granularity level (Campaign, Adset, Ad, ...) in the request|

See the documents below for a better understanding of the parameters:
- [Facebook API Insights documentation](https://developers.facebook.com/docs/marketing-api/insights)
- [API Reference for Ad Insights](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights/)
- [Available Fields for Nautilus](../helpers/facebook_helper.py)


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


| --googleads-developer-token | --googleads-client-id | --googleads-client-secret | --googleads-refresh-token | --googleads-manager-id | --googleads-client-customer-id  | --googleads-report-name | --googleads-report-type | --googleads-date-range-type | --googleads-start-date | --googleads-end-date | --googleads-field | --googleads-report-filter | --googleads-include-zero-impressions |
|:-----------------:|:---------------------:|:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:|:--------------------:|:---------------------------:|:----------------------:|:-------------------:|:-------------------------:|:----------------:|:------------------------:|:------------------------:|
|Company Developer token for Google Ads API |OAuth2 ID| OAuth2 Secret|Refresh token for OAuth2|Manager_Account_ID (XXX-XXX-XXXX identifier) (optional)|GAds_Account_ID (ignored if a manager account ID was given)|Optional Name for your output stream ("Custom Report" by default)|Type of Report to be called|Type of Date Range to apply (if "CUSTOM_RANGE", a min and max date must be specified) |Start Date for "CUSTOM_RANGE" date range (optional)|End Date for "CUSTOM_RANGE" date range (optional)|List of fields to request |Filter to apply on a chosen field (Dictionary as String "{'field':,'operator':,'values':}")|Boolean specifying whether or not rows with zero impressions should be included in report|

See the documents below for a better understanding of the parameters:
- [Google Ads API Reporting Basics](https://developers.google.com/adwords/api/docs/guides/reporting#create_a_report_definition)
- [Possible Date Ranges](https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges)


