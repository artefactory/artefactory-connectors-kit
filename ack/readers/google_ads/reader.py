# GNU Lesser General Public License v3.0 only
# Copyright (C) 2020 Artefact
# licence-information@artefact.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import ast
import codecs
import csv
import re
from io import StringIO

from click import ClickException
from ack.config import logger
from ack.readers.google_ads.config import DATEFORMAT, ENCODING
from ack.readers.reader import Reader
from ack.streams.json_stream import JSONStream
from ack.utils.exceptions import InconsistentDateDefinitionException, NoDateDefinitionException
from ack.utils.retry import retry

from googleads import adwords
from googleads.errors import AdWordsReportBadRequestError
from googleads.oauth2 import GoogleRefreshTokenClient


class GoogleAdsReader(Reader):
    def __init__(
        self,
        developer_token,
        client_id,
        client_secret,
        refresh_token,
        manager_id,
        client_customer_ids,
        report_name,
        report_type,
        date_range_type,
        start_date,
        end_date,
        fields,
        report_filter,
        include_zero_impressions,
        filter_on_video_campaigns,
        include_client_customer_id,
    ):
        self.developer_token = developer_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.oauth2_client = GoogleRefreshTokenClient(self.client_id, self.client_secret, self.refresh_token)
        self.manager_id = manager_id
        self.client_customer_ids = list(client_customer_ids)
        self.report_name = report_name
        self.report_type = report_type
        self.date_range_type = date_range_type
        self.start_date = start_date
        self.end_date = end_date
        self.fields = list(fields)
        self.report_filter = ast.literal_eval(report_filter)
        self.include_zero_impressions = include_zero_impressions
        self.filter_on_video_campaigns = filter_on_video_campaigns
        self.include_client_customer_id = include_client_customer_id
        self.download_format = "CSV"

    def init_adwords_client(self, id):
        return adwords.AdWordsClient(self.developer_token, self.oauth2_client, client_customer_id=id)

    @staticmethod
    def valid_client_customer_id(client_customer_id):
        return re.match(r"\d{3}-\d{3}-\d{4}", client_customer_id)

    @retry
    def fetch_report_from_gads_client_customer_obj(self, report_definition, client_customer_id):
        if not self.valid_client_customer_id(client_customer_id):
            raise ClickException(
                f"Invalid format: {client_customer_id}. Client customer ID should respect the following format 123-456-7890."
            )
        else:
            try:

                adwords_client = self.init_adwords_client(client_customer_id)
                report_downloader = adwords_client.GetReportDownloader()
                customer_report = report_downloader.DownloadReportAsStream(
                    report_definition,
                    client_customer_id=client_customer_id,
                    include_zero_impressions=self.include_zero_impressions,
                    skip_report_header=True,
                    skip_column_header=True,
                    skip_report_summary=True,
                )
                return customer_report
            except AdWordsReportBadRequestError as e:
                if e.type == "AuthorizationError.CUSTOMER_NOT_ACTIVE":
                    logger.warning(f"Skipping clientCustomerId {client_customer_id} (inactive).")
                else:
                    raise Exception(f"Wrong request. Error type: {e.type}")

    def get_customer_ids(self, manager_id):
        """Retrieves all CustomerIds in the account hierarchy.
        Note that your configuration file must specify a client_customer_id belonging
        to an AdWords manager account.
        Args:
        client: an AdWordsClient instance.
        Raises:
        Exception: if no CustomerIds could be found.
        Returns:
        A list of customer accounts
        """

        adwords_client = self.init_adwords_client(manager_id)
        managed_customer_service = adwords_client.GetService("ManagedCustomerService", version="v201809")

        offset = 0
        PAGE_SIZE = 500
        # Get the account hierarchy for this account.
        selector = {
            "fields": ["CustomerId"],
            "predicates": [{"field": "CanManageClients", "operator": "EQUALS", "values": [False]}],
            "paging": {"startIndex": str(offset), "numberResults": str(PAGE_SIZE)},
        }

        client_customer_ids = []
        more_pages = True

        while more_pages:
            page = managed_customer_service.get(selector)

            if page and "entries" in page and page["entries"]:
                for entry in page["entries"]:
                    client_customer_ids.append(self.format_customer_id(entry["customerId"]))
            else:
                raise Exception("Can't retrieve any customer ID.")
            offset += PAGE_SIZE
            selector["paging"]["startIndex"] = str(offset)
            more_pages = offset < int(page["totalNumEntries"])

        return [id for id in client_customer_ids if id]

    @staticmethod
    def format_customer_id(id):
        id_string = repr(id)
        formatted_id = id_string[:3] + "-" + id_string[3:6] + "-" + id_string[6:10]
        if not GoogleAdsReader.valid_client_customer_id(formatted_id):
            return None
        return formatted_id

    def get_report_definition(self):
        """Get required parameters for report fetching"""
        report_definition = {
            "reportName": self.report_name,
            "dateRangeType": self.date_range_type,
            "reportType": self.report_type,
            "downloadFormat": self.download_format,
            "selector": {"fields": self.fields},
        }
        self.add_period_to_report_definition(report_definition)
        self.add_report_filter(report_definition)
        return report_definition

    def add_period_to_report_definition(self, report_definition):
        """Add Date period from provided start date and end date, when CUSTOM DATE range is called"""
        if (self.date_range_type == "CUSTOM_DATE") & (not self.start_date or not self.end_date):
            raise NoDateDefinitionException(
                """You must define a couple
            start-date/end-date when using a custom_date"""
            )
        elif self.date_range_type == "CUSTOM_DATE":
            logger.info("Date format used for request : Custom Date Range with start_date and end_date provided")
            report_definition["selector"]["dateRange"] = self.create_date_range(self.start_date, self.end_date)
        elif self.start_date is not None and self.end_date is not None and self.date_range_type != "CUSTOM_DATE":
            raise InconsistentDateDefinitionException(
                "You must define either the couple start_date and end_date or a date_range, \
                    different from CUSTOM_DATE, but not both"
            )

    def add_report_filter(self, report_definition):
        """Check if a filter was provided and contains the necessary information"""
        if not self.report_filter:
            logger.info("No filter provided by user")

        elif all(required_param in self.report_filter.keys() for required_param in ("field", "operator", "values")):
            report_definition["selector"]["predicates"] = {
                "field": self.report_filter["field"],
                "operator": self.report_filter["operator"],
                "values": self.report_filter["values"],
            }
        else:
            raise ClickException(
                "Wrong format for Report filter : should be a dictionary as string, with the following fields:\n"
                "Dictionary {'field','operator','values'}"
            )

    @staticmethod
    def create_date_range(start_date, end_date):
        return {"min": start_date.strftime(DATEFORMAT), "max": end_date.strftime(DATEFORMAT)}

    def list_video_campaign_ids(self):
        video_campaign_report_definition = self.get_video_campaign_report_definition()
        stream_reader = codecs.getreader(ENCODING)

        video_campaign_ids = set()
        for googleads_account_id in self.client_customer_ids:
            customer_ids_report = self.fetch_report_from_gads_client_customer_obj(
                video_campaign_report_definition, googleads_account_id
            )
            customer_ids_report = stream_reader(customer_ids_report)
            for campaign_id in customer_ids_report:
                video_campaign_ids.add(campaign_id.replace("\n", ""))
        return video_campaign_ids

    def get_video_campaign_report_definition(self):
        if "CampaignId" not in self.fields:
            raise ClickException("Filter On Video Campaigns is only available if 'CampaignId' is requested as a report field")
        video_campaigns_report = {
            "reportName": "video campaigns ids",
            "dateRangeType": self.date_range_type,
            "reportType": "VIDEO_PERFORMANCE_REPORT",
            "downloadFormat": self.download_format,
            "selector": {"fields": "CampaignId"},
        }
        self.add_period_to_report_definition(video_campaigns_report)
        return video_campaigns_report

    def format_and_yield(self):
        report_definition = self.get_report_definition()
        stream_reader = codecs.getreader(ENCODING)
        if self.filter_on_video_campaigns:
            video_campaign_ids = self.list_video_campaign_ids()

        for googleads_account_id in self.client_customer_ids:
            customer_report = self.fetch_report_from_gads_client_customer_obj(report_definition, googleads_account_id)
            if customer_report:
                customer_report = stream_reader(customer_report)
                for row in customer_report:
                    reader = csv.DictReader(StringIO(row), self.fields)
                    for row in reader:
                        if self.include_client_customer_id:
                            row["AccountId"] = googleads_account_id
                        if self.filter_on_video_campaigns:
                            if row["CampaignId"] in video_campaign_ids:
                                yield row
                        else:
                            yield row

    def read(self):
        if self.manager_id:
            self.client_customer_ids = self.get_customer_ids(self.manager_id)

        yield JSONStream("results_" + self.report_name + "_" + "_".join(self.client_customer_ids), self.format_and_yield())
