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
import click
from nck.config import logger

import sys
import traceback
import time
import numpy as np
from datetime import datetime, timedelta

from typing import List, Dict, Tuple
from typing import NamedTuple
from collections import OrderedDict

from nck.readers import Reader
from nck.commands.command import processor
from nck.streams.json_stream import JSONStream
from nck.utils.retry import retry
from nck.utils.args import extract_args

from radarly import RadarlyApi
from radarly.project import Project
from radarly.parameters import SearchPublicationParameter as Payload


class DateRangeSplit(NamedTuple):
    date_ranges_and_posts_volumes: Dict[Tuple[datetime, datetime], int]
    is_compliant: bool


@click.command(name="read_radarly")
@click.option("--radarly-pid", required=True, type=click.INT, help="Radarly Project ID")
@click.option("--radarly-client-id", required=True, type=click.STRING)
@click.option("--radarly-client-secret", required=True, type=click.STRING)
@click.option(
    "--radarly-focus-id",
    required=True,
    multiple=True,
    type=click.INT,
    help="Focus IDs (from Radarly queries)",
)
@click.option(
    "--radarly-start-date",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]),
)
@click.option(
    "--radarly-end-date",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]),
)
@click.option(
    "--radarly-api-request-limit",
    default=250,
    type=click.INT,
    help="Max number of posts per API request",
)
@click.option(
    "--radarly-api-date-period-limit",
    default=int(1e4),
    type=click.INT,
    help="Max number of posts in a single API search query",
)
@click.option(
    "--radarly-api-quarterly-posts-limit",
    default=int(45e3),
    type=click.INT,
    help="Max number of posts requested in the window (usually 15 min) (see Radarly documentation)",
)
@click.option(
    "--radarly-api-window",
    default=300,
    type=click.INT,
    help="Duration of the window (usually 300 seconds)",
)
@click.option(
    "--radarly-throttle",
    default=True,
    type=click.BOOL,
    help="""If set to True, forces the connector to abide by official Radarly API limitations
         (using the api-quarterly-posts-limit parameter)""",
)
@click.option("--radarly-throttling-threshold-coefficient", default=0.95, type=click.FLOAT)
@processor("radarly_client_id", "radarly_client_secret")
def radarly(**kwargs):
    return RadarlyReader(**extract_args("radarly_", kwargs))


class RadarlyReader(Reader):
    def __init__(
        self,
        pid: int,
        client_id: str,
        client_secret: str,
        focus_id: Tuple[int, ...],
        start_date: datetime,
        end_date: datetime,
        api_request_limit: int,
        api_date_period_limit: int,
        api_quarterly_posts_limit: int,
        api_window: int,
        throttle: bool,
        throttling_threshold_coefficient: float,
    ):

        self.api_request_limit = api_request_limit
        self.api_date_period_limit = api_date_period_limit
        self.api_quarterly_posts_limit = api_quarterly_posts_limit
        self.api_window = api_window

        RadarlyApi.init(client_id=client_id, client_secret=client_secret)

        self.pid = pid
        self.project = self.get_project(pid=self.pid)
        self.focus_ids: List[int] = list(focus_id)

        self.start_date = start_date
        self.end_date = end_date

        self.throttle = throttle
        self.throttling_threshold_coefficient = throttling_threshold_coefficient

    def read(self):
        """
        :return: stream that returns Radarly posts one by one
        """
        date_ranges_and_posts_volumes: Dict = self.split_date_range()
        logger.info(f"API Compliant Date Ranges and Posts Volumes: {date_ranges_and_posts_volumes}")
        api_compliant_date_ranges = list(date_ranges_and_posts_volumes.keys())

        t0 = time.time()
        ingestion_tracker = []

        for i, date_range in enumerate(api_compliant_date_ranges):

            if self.throttle:
                current_time = time.time() - t0
                ingestion_tracker.append(current_time)
                posts_ingested_over_window = (
                    sum(np.array(ingestion_tracker) > current_time - self.api_window) * self.api_date_period_limit
                )
                if posts_ingested_over_window > self.throttling_threshold_coefficient * self.api_quarterly_posts_limit:
                    sleep_duration = self.api_window * (self.api_date_period_limit / self.api_quarterly_posts_limit)
                    logger.info(f"Throttling activated: waiting for {sleep_duration} seconds...")
                    time.sleep(sleep_duration)

            all_publications = self.get_publications_iterator(date_range)
            name = f"""radarly_{date_range[0].strftime("%Y-%m-%d-%H-%M-%S")}_{date_range[1].strftime(
                "%Y-%m-%d-%H-%M-%S")}"""

            def result_generator():
                while True:
                    try:
                        pub = next(all_publications)
                        yield dict(pub)
                    except StopIteration:
                        break
                    except Exception:
                        ex_type, ex, tb = sys.exc_info()
                        logger.warning(f"Failed to ingest post with error: {ex}. Traceback: {traceback.print_tb(tb)}")

            yield JSONStream(name, result_generator())

    @retry
    def get_publications_iterator(self, date_range: Tuple[datetime, datetime]):
        param = self.get_payload(date_range[0], date_range[1])
        all_publications = self.project.get_all_publications(param)
        logger.info(f"Getting posts from {date_range[0]} to {date_range[1]}")
        return all_publications

    @staticmethod
    @retry
    def get_project(pid: int):
        return Project.find(pid=pid)

    def get_payload(self, start_date: datetime, end_date: datetime):
        param = (
            Payload()
            .creation_date(created_after=start_date, created_before=end_date)
            .focuses(self.focus_ids)
            .pagination(start=0, limit=self.api_request_limit)
        )
        return param

    @retry
    def get_posts_volume(self, first_date: datetime, second_date: datetime) -> int:
        param = self.get_payload(first_date, second_date)
        posts_volume = self.project.get_all_publications(param).total
        return posts_volume

    def get_total_posts_volume(self) -> int:
        return self.get_posts_volume(first_date=self.start_date, second_date=self.end_date)

    def get_posts_volumes_from_list(
        self, date_ranges: List[Tuple[datetime, datetime]]
    ) -> Dict[Tuple[datetime, datetime], int]:
        posts_volumes = OrderedDict()
        for date_range in date_ranges:
            first_date, second_date = date_range
            posts_volume = self.get_posts_volume(first_date=first_date, second_date=second_date)
            posts_volumes[date_range] = posts_volume
        return posts_volumes

    def split_date_range(self) -> Dict[Tuple[datetime, datetime], int]:
        total_count = self.get_total_posts_volume()
        logger.info(f"Posts Total Count: {total_count}")
        return self._split_date_range_auxiliary(self.start_date, self.end_date, posts_count=total_count)

    def _split_date_range_auxiliary(
        self, first_date: datetime, second_date: datetime, posts_count: int
    ) -> Dict[Tuple[datetime, datetime], int]:
        if posts_count < self.api_date_period_limit:
            logger.debug(f"Direct Return: {[first_date, second_date]}")
            return OrderedDict({(first_date, second_date): posts_count})

        else:

            date_range_split: DateRangeSplit = self.generate_DateRangeSplit_object(
                date_range_start=first_date,
                date_range_end=second_date,
                posts_count=posts_count,
                extra_margin=1,
            )
            date_ranges_and_posts_volumes: Dict[
                Tuple[datetime, datetime], int
            ] = date_range_split.date_ranges_and_posts_volumes
            is_compliant: bool = date_range_split.is_compliant

            if is_compliant:
                res = date_ranges_and_posts_volumes
            else:
                res = OrderedDict()
                for date_range, vol in date_ranges_and_posts_volumes.items():
                    if vol < self.api_date_period_limit:
                        res.update({date_range: vol})
                    else:
                        res.update(self._split_date_range_auxiliary(*date_range, posts_count=vol))
            return res

    def generate_DateRangeSplit_object(
        self,
        date_range_start: datetime,
        date_range_end: datetime,
        posts_count: int,
        extra_margin=1,
    ) -> DateRangeSplit:

        delta = date_range_end - date_range_start
        split_count_guess = posts_count // self.api_date_period_limit + delta.days + extra_margin
        split_range_guess = delta.total_seconds() // split_count_guess

        date_ranges_guess = self._generate_date_ranges(date_range_start, date_range_end, split_range_guess, split_count_guess)
        date_ranges_and_posts_volumes = self.get_posts_volumes_from_list(date_ranges_guess)
        is_compliant = all(np.fromiter(date_ranges_and_posts_volumes.values(), dtype=int) <= self.api_date_period_limit)

        return DateRangeSplit(date_ranges_and_posts_volumes, is_compliant)

    @staticmethod
    def _generate_date_ranges(
        start_date: datetime, end_date: datetime, split_range: float, split_count: int
    ) -> List[Tuple[datetime, datetime]]:
        res = [
            (
                start_date + i * timedelta(seconds=split_range),
                start_date + (i + 1) * timedelta(seconds=split_range),
            )
            for i in range(split_count - 1)
        ]
        res += [(start_date + (split_count - 1) * timedelta(seconds=split_range), end_date)]

        return res
