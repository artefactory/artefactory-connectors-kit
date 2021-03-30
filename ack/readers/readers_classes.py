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
from ack.readers.adobe_analytics_1_4.config import AdobeAnalytics14ReaderConfig
from ack.readers.adobe_analytics_2_0.config import AdobeAnalytics20ReaderConfig
from ack.readers.amazon_s3.config import AmazonS3ReaderConfig
from ack.readers.confluence.config import ConfluenceReaderConfig
from ack.readers.facebook.config import FacebookReaderConfig
from ack.readers.google_ads.config import GoogleAdsReaderConfig
from ack.readers.google_analytics.config import GoogleAnalyticsReaderConfig
from ack.readers.google_cloud_storage.config import GoogleCloudStorageReaderConfig
from ack.readers.google_dbm.config import GoogleDBMReaderConfig
from ack.readers.google_dcm.config import GoogleDCMReaderConfig
from ack.readers.google_dv360.config import GoogleDV360ReaderConfig
from ack.readers.google_sa360.config import GoogleSA360ReaderConfig
from ack.readers.google_search_console.config import GoogleSearchConsoleReaderConfig
from ack.readers.google_sheets.config import GoogleSheetsReaderConfig
from ack.readers.google_sheets_old.config import GoogleSheetsReaderOldConfig
from ack.readers.mysql.config import MySQLReaderConfig
from ack.readers.mytarget.config import MyTargetReaderConfig
from ack.readers.radarly.config import RadarlyReaderConfig
from ack.readers.adobe_analytics_1_4.reader import AdobeAnalytics14Reader
from ack.readers.adobe_analytics_2_0.reader import AdobeAnalytics20Reader
from ack.readers.amazon_s3.reader import AmazonS3Reader
from ack.readers.confluence.reader import ConfluenceReader
from ack.readers.facebook.reader import FacebookReader
from ack.readers.google_ads.reader import GoogleAdsReader
from ack.readers.google_analytics.reader import GoogleAnalyticsReader
from ack.readers.google_cloud_storage.reader import GoogleCloudStorageReader
from ack.readers.google_dbm.reader import GoogleDBMReader
from ack.readers.google_dcm.reader import GoogleDCMReader
from ack.readers.google_dv360.reader import GoogleDV360Reader
from ack.readers.google_sa360.reader import GoogleSA360Reader
from ack.readers.google_search_console.reader import GoogleSearchConsoleReader
from ack.readers.google_sheets.reader import GoogleSheetsReader
from ack.readers.google_sheets_old.reader import GoogleSheetsReaderOld
from ack.readers.mysql.reader import MySQLReader
from ack.readers.mytarget.reader import MyTargetReader
from ack.readers.radarly.reader import RadarlyReader
from ack.readers.salesforce.config import SalesforceReaderConfig
from ack.readers.salesforce.reader import SalesforceReader
from ack.readers.the_trade_desk.config import TheTradeDeskReaderConfig
from ack.readers.the_trade_desk.reader import TheTradeDeskReader
from ack.readers.twitter.config import TwitterReaderConfig
from ack.readers.twitter.reader import TwitterReader
from ack.readers.yandex_campaign.config import YandexCampaignReaderConfig
from ack.readers.yandex_campaign.reader import YandexCampaignReader
from ack.readers.yandex_statistics.config import YandexStatisticsReaderConfig
from ack.readers.yandex_statistics.reader import YandexStatisticsReader


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
