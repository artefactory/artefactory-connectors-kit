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
from nck.readers.adobe_analytics_1_4.config import AdobeAnalytics14ReaderConfig
from nck.readers.adobe_analytics_2_0.config import AdobeAnalytics20ReaderConfig
from nck.readers.amazon_s3.config import AmazonS3ReaderConfig
from nck.readers.confluence.config import ConfluenceReaderConfig
from nck.readers.facebook.config import FacebookReaderConfig
from nck.readers.google_ads.config import GoogleAdsReaderConfig
from nck.readers.google_analytics.config import GoogleAnalyticsReaderConfig
from nck.readers.google_cloud_storage.config import GoogleCloudStorageReaderConfig
from nck.readers.google_dbm.config import GoogleDBMReaderConfig
from nck.readers.google_dcm.config import GoogleDCMReaderConfig
from nck.readers.google_dv360.config import GoogleDV360ReaderConfig
from nck.readers.google_sa360.config import GoogleSA360ReaderConfig
from nck.readers.google_search_console.config import GoogleSearchConsoleReaderConfig
from nck.readers.google_sheets.config import GoogleSheetsReaderConfig
from nck.readers.google_sheets_old.config import GoogleSheetsReaderOldConfig
from nck.readers.mysql.config import MySQLReaderConfig
from nck.readers.mytarget.config import MyTargetReaderConfig
from nck.readers.radarly.config import RadarlyReaderConfig
from nck.readers.reader import Reader
from nck.readers.adobe_analytics_1_4.reader import AdobeAnalytics14Reader
from nck.readers.adobe_analytics_2_0.reader import AdobeAnalytics20Reader
from nck.readers.amazon_s3.reader import AmazonS3Reader
from nck.readers.confluence.reader import ConfluenceReader
from nck.readers.facebook.reader import FacebookReader
from nck.readers.google_ads.reader import GoogleAdsReader
from nck.readers.google_analytics.reader import GoogleAnalyticsReader
from nck.readers.google_cloud_storage.reader import GoogleCloudStorageReader
from nck.readers.google_dbm.reader import GoogleDBMReader
from nck.readers.google_dcm.reader import GoogleDCMReader
from nck.readers.google_dv360.reader import GoogleDV360Reader
from nck.readers.google_sa360.reader import GoogleSA360Reader
from nck.readers.google_search_console.reader import GoogleSearchConsoleReader
from nck.readers.google_sheets.reader import GoogleSheetsReader
from nck.readers.google_sheets_old.reader import GoogleSheetsReaderOld
from nck.readers.mysql.reader import MySQLReader
from nck.readers.mytarget.reader import MyTargetReader
from nck.readers.radarly.reader import RadarlyReader
from nck.readers.adobe_analytics_1_4.cli import adobe_analytics_1_4
from nck.readers.adobe_analytics_2_0.cli import adobe_analytics_2_0
from nck.readers.amazon_s3.cli import amazon_s3
from nck.readers.confluence.cli import confluence
from nck.readers.facebook.cli import facebook
from nck.readers.google_ads.cli import google_ads
from nck.readers.google_analytics.cli import google_analytics
from nck.readers.google_cloud_storage.cli import google_cloud_storage
from nck.readers.google_dbm.cli import google_dbm
from nck.readers.google_dcm.cli import google_dcm
from nck.readers.google_dv360.cli import google_dv360
from nck.readers.google_sa360.cli import google_sa360
from nck.readers.google_search_console.cli import google_search_console
from nck.readers.google_sheets.cli import google_sheets
from nck.readers.google_sheets_old.cli import google_sheets_old
from nck.readers.mysql.cli import mysql
from nck.readers.mytarget.cli import mytarget
from nck.readers.radarly.cli import radarly
from nck.readers.salesforce.cli import salesforce
from nck.readers.salesforce.config import SalesforceReaderConfig
from nck.readers.salesforce.reader import SalesforceReader
from nck.readers.the_trade_desk.cli import the_trade_desk
from nck.readers.the_trade_desk.config import TheTradeDeskReaderConfig
from nck.readers.the_trade_desk.reader import TheTradeDeskReader
from nck.readers.twitter.cli import twitter
from nck.readers.twitter.config import TwitterReaderConfig
from nck.readers.twitter.reader import TwitterReader
from nck.readers.yandex_campaign.cli import yandex_campaigns
from nck.readers.yandex_campaign.config import YandexCampaignReaderConfig
from nck.readers.yandex_campaign.reader import YandexCampaignReader
from nck.readers.yandex_statistics.cli import yandex_statistics
from nck.readers.yandex_statistics.config import YandexStatisticsReaderConfig
from nck.readers.yandex_statistics.reader import YandexStatisticsReader

readers = [
    adobe_analytics_1_4,
    adobe_analytics_2_0,
    amazon_s3,
    confluence,
    facebook,
    google_ads,
    google_analytics,
    google_cloud_storage,
    google_dbm,
    google_dcm,
    google_dv360,
    google_sa360,
    google_search_console,
    google_sheets,
    google_sheets_old,
    mysql,
    mytarget,
    radarly,
    salesforce,
    the_trade_desk,
    twitter,
    yandex_campaigns,
    yandex_statistics,
]

reader_classes = {
    "adobe_analytics_1_4": (AdobeAnalytics14Reader, AdobeAnalytics14ReaderConfig),
    "adobe_analytics_2_0": (AdobeAnalytics20Reader, AdobeAnalytics20ReaderConfig),
    "amazon_s3": (AmazonS3Reader, AmazonS3ReaderConfig),
    "confluence": (ConfluenceReader, ConfluenceReaderConfig),
    "facebook": (FacebookReader, FacebookReaderConfig),
    "google_ads": (GoogleAdsReader, GoogleAdsReaderConfig),
    "google_analytics": (GoogleAnalyticsReader, GoogleAnalyticsReaderConfig),
    "google_cloud_storage": (GoogleCloudStorageReader, GoogleCloudStorageReaderConfig),
    "google_dbm": (GoogleDBMReader, GoogleDBMReaderConfig),
    "google_dcm": (GoogleDCMReader, GoogleDCMReaderConfig),
    "google_dv360": (GoogleDV360Reader, GoogleDV360ReaderConfig),
    "google_sa360": (GoogleSA360Reader, GoogleSA360ReaderConfig),
    "google_search_console": (GoogleSearchConsoleReader, GoogleSearchConsoleReaderConfig),
    "google_sheets": (GoogleSheetsReader, GoogleSheetsReaderConfig),
    "google_sheets_old": (GoogleSheetsReaderOld, GoogleSheetsReaderOldConfig),
    "mysql": (MySQLReader, MySQLReaderConfig),
    "mytarget": (MyTargetReader, MyTargetReaderConfig),
    "radarly": (RadarlyReader, RadarlyReaderConfig),
    "salesforce": (SalesforceReader, SalesforceReaderConfig),
    "the_trade_desk": (TheTradeDeskReader, TheTradeDeskReaderConfig),
    "twitter": (TwitterReader, TwitterReaderConfig),
    "yandex_campaign": (YandexCampaignReader, YandexCampaignReaderConfig),
    "yandex_statistics": (YandexStatisticsReader, YandexStatisticsReaderConfig),
}


__all__ = ["readers", "Reader", "reader_classes"]
