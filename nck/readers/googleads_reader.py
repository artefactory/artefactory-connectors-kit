import logging
import click
import re
import yaml
import codecs

from itertools import chain
from click import ClickException

from nck.readers.reader import Reader
from nck.utils.args import extract_args
from nck.commands.command import processor
from nck.streams.normalized_json_stream import NormalizedJSONStream
from nck.helpers.googleads_helper import (
    REPORT_TYPE_POSSIBLE_VALUES,
    DATE_RANGE_TYPE_POSSIBLE_VALUES,
)

import googleads.adwords


DATEFORMAT = "%Y%m%d"

@click.command(name="read_googleads")
@click.option("--googleads-developer-token",required=True)
@click.option("--googleads-client-id",required=True)
@click.option("--googleads-client-secret",required=True)
@click.option("--googleads-refresh-token", required=True)
@click.option(
    "--googleads-client-customer-id",
    multiple=True,
    required=True,
    help="Google Ads Client Account(s) to be called, thanks to their IDs",
)
@click.option(
    "--googleads-report-name",
    default="Custom Report",
    help="Name given to your Report",
)
@click.option(
    "--googleads-report-type",
    type=click.Choice(REPORT_TYPE_POSSIBLE_VALUES),
    default=REPORT_TYPE_POSSIBLE_VALUES[0],
    help="Desired Report Type to fetch\n"
    "https://developers.google.com/adwords/api/docs/appendix/reports#available-reports",
)
@click.option(
    "--googleads-date-range-type",
    type=click.Choice(DATE_RANGE_TYPE_POSSIBLE_VALUES),
    default=DATE_RANGE_TYPE_POSSIBLE_VALUES[0],
    help="Desired Date Range Type to fetch\n"
    "https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges",
)
@click.option(
    "--googleads-start-date", 
    type=click.DateTime(),
    default="",
)
@click.option(
    "--googleads-end-date", 
    type=click.DateTime(),
    default="",
)
@click.option(
    "--googleads-field", 
    multiple=True, 
    help="Google Ads API fields for the request\n"
    "https://developers.google.com/adwords/api/docs/appendix/reports#available-reports"
)
@click.option(
    "--googleads-report-filter", 
    default=None, 
    help="A filter can be applied on a chosen field, in the form of a Dictionary {'field','operator','values'}\n"
    "https://developers.google.com/adwords/api/docs/guides/reporting#create_a_report_definition"
)
@processor("googleads_developer_token", "googleads_app_secret", "googleads_refresh_token")

def google_ads(**kwargs):
    return GoogleAdsReader(**extract_args("googleads_", kwargs))


class GoogleAdsReader(Reader):
    def __init__(
        self,
        developer_token,
        client_id,
        client_secret,
        refresh_token,
        client_customer_id,
        report_name,
        report_type,
        date_range_type,
        start_date,
        end_date,
        field,
        report_filter,
    ):
        self.developer_token = developer_token
        self.credentials_dict = {
            'adwords':{
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'developer_token': self.developer_token,
                'client_customer_id': self.client_customer_ids[0],
            }
        }
        self.client_customer_ids = list(client_customer_id)
        self.report_name = report_name
        self.report_type = report_type
        self.date_range_type = date_range_type
        self.start_date = start_date
        self.end_date = end_date
        self.fields = list(field)
        self.report_filter = report_filter
        self.download_format = "CSV"

    @retry
    def fetch_report_from_gads_client_customer_obj(self, report_definition, client_customer_id):
        if re.match(r"\d{3}-\d{3}-\d{4}",client_customer_id):
            customer_report = report_downloader.DownloadReportAsStream(
                report_definition,
                client_customer_id=client_customer_id,
                skip_report_header=True,
                skip_column_header=True,
                skip_report_summary=True,
            )
            stream_reader = codecs.getreader(encoding)
            customer_report = stream_reader(customer_report)
        else:
            raise ClickException("Wrong format. Client Account ID should be a 'ddd-ddd-dddd' pattern, with digits separated by dashes")
        
        return customer_report

    @retry
    def run_query_on_fb_campaign_obj_conf(self, params, ad_object_id, recurse_level):
        campaign = Campaign(ad_object_id)
        if recurse_level <= 0:
            val_cmp = campaign.api_get(fields=CMP_POSSIBLE_VALUES, params=params)
            yield val_cmp

        else:
            for el in chain(
                *[
                    self.run_query_on_fb_adset_obj_conf(
                        params, adset.get("id"), recurse_level - 1
                    )
                    for adset in campaign.get_ad_sets()
                ]
            ):
                yield el

    @retry
    def run_query_on_fb_adset_obj_conf(self, params, ad_object_id, recurse_level):
        adset = AdSet(ad_object_id)
        if recurse_level <= 0:
            val_adset = adset.api_get(fields=ADS_POSSIBLE_VALUES, params=params)
            yield val_adset
        else:
            raise ClickException(
                "for now, just campaign object and adset object are able to be requested without insights"
            )


    def get_customer_ids(self, client):
        """Retrieves all CustomerIds in the account hierarchy.
        Note that your configuration file must specify a client_customer_id belonging
        to an AdWords manager account.
        Args:
        client: an AdWordsClient instance.
        Raises:
        Exception: if no CustomerIds could be found.
        Returns:
        A Queue instance containing all CustomerIds in the account hierarchy.
        """
        # For this example, we will use ManagedCustomerService to get all IDs in
        # hierarchy that do not belong to MCC accounts.
        managed_customer_service = client.GetService('ManagedCustomerService',
                                                   version='v201809')

        offset = 0

        # Get the account hierarchy for this account.
        selector = {
          'fields': ['CustomerId'],
          'predicates': [{
              'field': 'CanManageClients',
              'operator': 'EQUALS',
              'values': [False]
          }],
          'paging': {
              'startIndex': str(offset),
              'numberResults': str(PAGE_SIZE)
          }
        }

        # Using Queue to balance load between processes.
        client_customer_ids = []
        more_pages = True

        while more_pages:
        page = managed_customer_service.get(selector)

        if page and 'entries' in page and page['entries']:
          for entry in page['entries']:
            client_customer_ids.append(entry['customerId'])
        else:
          raise Exception('Can\'t retrieve any customer ID.')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])

        self.client_customer_ids = client_customer_ids


    def get_report_definition(self):
        """Get required parameters for report fetching"""
        report_definition = {
            "reportName": self.report_name,
            "dateRangeType": self.date_range_type,
            "reportType": self.report_type,
            "downloadFormat": self.download_format,
            "selector": {
                "fields": self.fields,
            },
        }
        self.add_period_to_report_definition(report_definition)
        self.add_report_filter(report_definition)
        return report_definition


    def add_period_to_report_definition(self, report_definition):
        """Add Date period from provided start date and end date, when CUSTOM DATE range is called"""
        if (self.date_range_type=="CUSTOM_DATE") & (not self.start_date or not self.end_date):
            logging.warning("⚠️ Custom Date Range selected but No date range provided - Select another DateRangeType or provide start and end dates ⚠️")
            logging.warning(
                "https://developers.google.com/adwords/api/docs/guides/reporting#custom_date_ranges"
            )
        elif self.date_range_type=="CUSTOM_DATE":
            logging.info("ℹ️ Date format used for request : Custom Date Range with start_date and end_date provided")
            report_definition["selector"]["dateRange"] = self.create_date_range(
                self.start_date, self.end_date
            )


    def add_report_filter(self, report_definition):
        """Check if a filter was provided and contains the necessary information"""
        if not self.report_filter:
            logging.info("ℹ️ No filter provided by user")
        elif all(required_param in self.report_filter for required_param in ('field','operator','values')):
            report_definition["selector"]["predicates"] = {
                'field': self.report_filter['field'],
                'operator': self.report_filter['operator'],
                'values': self.report_filter['values'],
            }
        else:
            logging.warning("⚠️ A Report filter was provided but is missing necessary information - Dictionary {'field','operator','values'} ⚠️")

    @staticmethod
    def create_date_range(start_date, end_date):
        return {
            "min": start_date.strftime(DATEFORMAT),
            "max": end_date.strftime(DATEFORMAT),
        }


    def format_and_yield(self, record):
        yield {field: get_field_value(record, field) for field in self.desired_fields}


    def result_generator(self, data):
        for record in data:
            yield from self.format_and_yield(record.export_all_data())


    def read(self):
        client = googleads.adwords.AdWordsClient.LoadFromString(yaml.dump(self.credentials_dict))

        report_definition = self.get_report_definition()
        report_downloader = client.GetReportDownloader()

        for googleads_account_id in self.client_customer_ids:

            customer_report = self.fetch_report_from_gads_client_customer_obj(report_definition, googleads_account_id)

            

        ################################# MAP whether report or metadata
        if self.ad_insights:
            query_mapping = {AD_OBJECT_TYPES[0]: self.run_query_on_fb_account_obj}
            args = [params, self.ad_object_id]
        else:
            query_mapping = {
                AD_OBJECT_TYPES[1]: self.run_query_on_fb_campaign_obj_conf,
                AD_OBJECT_TYPES[2]: self.run_query_on_fb_adset_obj_conf,
            }
            args = [params, self.ad_object_id, self.recurse_level]
        try:
            query = query_mapping[self.ad_object_type]
            data = query(*args)
        except KeyError:
            raise ClickException(
                "`{}` is not a valid adObject type".format(self.ad_object_type)
            )
        #################################

        yield NormalizedJSONStream(
            "results_" + self.report_name + "_" + str(self.ad_object_id),
            self.result_generator(data),
        )

if __name__ == '__main__':

    client = googleads.adwords.AdWordsClient.LoadFromStorage()

