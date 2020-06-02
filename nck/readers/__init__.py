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
from nck.readers.reader import Reader

from nck.readers.mysql_reader import mysql
from nck.readers.gcs_reader import gcs
from nck.readers.googleads_reader import google_ads
from nck.readers.s3_reader import s3
from nck.readers.sa360_reader import sa360_reader
from nck.readers.oracle_reader import oracle
from nck.readers.gsheets_reader import gsheets
from nck.readers.salesforce_reader import salesforce
from nck.readers.facebook_reader import facebook
from nck.readers.dbm_reader import dbm
from nck.readers.dcm_reader import dcm
from nck.readers.ga_reader import ga
from nck.readers.search_console_reader import search_console
from nck.readers.adobe_reader import adobe
from nck.readers.adobe_reader_2_0 import adobe_2_0
from nck.readers.radarly_reader import radarly
from nck.readers.yandex_campaign_reader import yandex_campaigns
from nck.readers.yandex_statistics_reader import yandex_statistics

readers = [
    mysql,
    salesforce,
    gsheets,
    gcs,
    google_ads,
    s3,
    sa360_reader,
    facebook,
    oracle,
    dbm,
    dcm,
    ga,
    search_console,
    adobe,
    adobe_2_0,
    radarly,
    yandex_campaigns,
    yandex_statistics
]


__all__ = ["readers", "Reader"]
