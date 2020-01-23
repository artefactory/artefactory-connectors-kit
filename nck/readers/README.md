# NCK Readers

Each reader role is to read data from external source and transform it into a Stream understable format to be written on GCS and BQ thanks to the corresponding writers.

## Step to create a new Reader

1. Create python module following naming nomenclature ``` [command]_reader.py ```
2. Implement `read` method
3. Create click command with required options
4. Reference click command into [commands list](./__init__.py)
5. Update current README.md

## Readers

### Facebook Reader

- Example

The following command retrieves some insights of every Ads in the Facebook account <ACCOUNT_ID> thanks to
a Facebook App whose access_token is <ACCESS_TOKEN>.

```
python bin/run.py read_facebook --facebook-access-token <ACCESS_TOKEN> --facebook-ad-object-id <ACCOUNT_ID> --facebook-breakdown gender --facebook-ad-level ad --facebook-start-date 2019-01-01 --facebook-end-date 2019-01-01 --facebook-field date_start --facebook-field date_stop --facebook-field account_currency --facebook-field account_id --facebook-field account_name --facebook-field ad_id --facebook-field ad_name --facebook-field adset_id --facebook-field adset_name --facebook-field campaign_id --facebook-field campaign_name --facebook-field clicks --facebook-field impressions --facebook-desired-field date_start --facebook-desired-field date_stop --facebook-desired-field account_name --facebook-desired-field account_id --facebook-desired-field ad_id --facebook-desired-field ad_namefacebook-desired-field clicks --facebook-desired-field impressions write_console
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







