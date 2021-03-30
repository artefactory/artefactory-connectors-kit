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
from ack.readers.reader import Reader
from ack.readers.adobe_analytics_1_4.cli import adobe_analytics_1_4
from ack.readers.adobe_analytics_2_0.cli import adobe_analytics_2_0
from ack.readers.amazon_s3.cli import amazon_s3
from ack.readers.confluence.cli import confluence
from ack.readers.facebook.cli import facebook
from ack.readers.google_ads.cli import google_ads
from ack.readers.google_analytics.cli import google_analytics
from ack.readers.google_cloud_storage.cli import google_cloud_storage
from ack.readers.google_dbm.cli import google_dbm
from ack.readers.google_dcm.cli import google_dcm
from ack.readers.google_dv360.cli import google_dv360
from ack.readers.google_sa360.cli import google_sa360
from ack.readers.google_search_console.cli import google_search_console
from ack.readers.google_sheets.cli import google_sheets
from ack.readers.google_sheets_old.cli import google_sheets_old
from ack.readers.mysql.cli import mysql
from ack.readers.mytarget.cli import mytarget
from ack.readers.radarly.cli import radarly
from ack.readers.salesforce.cli import salesforce
from ack.readers.the_trade_desk.cli import the_trade_desk
from ack.readers.twitter.cli import twitter
from ack.readers.yandex_campaign.cli import yandex_campaigns
from ack.readers.yandex_statistics.cli import yandex_statistics
from ack.readers.readers_classes import reader_classes


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

__all__ = ["readers", "Reader", "reader_classes"]
