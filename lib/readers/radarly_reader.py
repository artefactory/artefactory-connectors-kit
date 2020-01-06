import click

import logging
import numpy as np
from datetime import datetime, timedelta
import sys
import traceback
import time
from radarly import RadarlyApi
from radarly.project import Project
from radarly.parameters import SearchPublicationParameter as Payload
from typing import List, Dict, Tuple
from typing import NamedTuple
from collections import OrderedDict


class DateRange(NamedTuple):
    daily_posts_volumes: Dict[Tuple[datetime, datetime], int]
    is_compliant: bool

import config
from lib.readers import Reader
from lib.commands.command import processor
from lib.streams.normalized_json_stream import NormalizedJSONStream
from lib.utils.retry import retry
from lib.utils.args import extract_args


@click.command(name="read_radarly")
@click.option("--radarly-pid", required=True)
@click.option("--radarly-focus-id", required=True, multiple=True, type=int)
@click.option("--radarly-start-date", required=True, type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ"]))
@click.option("--radarly-end-date", required=True, type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ"]))
@click.option("--radarly-api-request-limit", default=250, type=int)
@click.option("--radarly-api-date-period-limit", default=int(1e4), type=int)
@click.option("--radarly-api-quarterly-posts-limit", default=int(45e3), type=int)
@click.option("--radarly-api-time-sleep", default=300, type=int)
@click.option("--radarly-throttle", default=True, type=bool)
@click.option("--radarly-throttling-threshold-coefficient", default=0.95, type=float)
@processor()
def radarly(**kwargs):
    return RadarlyReader(**extract_args('radarly_', kwargs))


class RadarlyReader(Reader):

    def __init__(self, pid: int, focus_id: Tuple[int], start_date: datetime, end_date: datetime,
                 api_request_limit: int,
                 api_date_period_limit: int,
                 api_quarterly_posts_limit: int,
                 api_time_sleep: int,
                 throttle: bool,
                 throttling_threshold_coefficient: float):

        self.api_request_limit = api_request_limit
        self.api_date_period_limit = api_date_period_limit
        self.api_quarterly_posts_limit = api_quarterly_posts_limit
        self.api_time_sleep = api_time_sleep

        RadarlyApi.init(client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET)

        self.pid = pid
        self.project = self.find_project(pid=self.pid)
        self.focus_ids = list(focus_id)
        logging.debug(f'Focus ids {self.focus_ids}')

        self.start_date = start_date
        self.end_date = end_date

        self.throttle = throttle
        self.throttling_threshold_coefficient = throttling_threshold_coefficient

    def read(self):
        """
        :return: stream that returns Radarly posts one by one
        """
        api_compliant_date_ranges: Dict = self.split_date_range()
        logging.info(f'API Compliant Date Ranges: {api_compliant_date_ranges}')
        api_compliant_date_ranges = list(api_compliant_date_ranges.keys())

        t0 = time.time()
        ingestion_tracker = []

        for i, date_range in enumerate(api_compliant_date_ranges):

            if self.throttle:
                current_time = time.time() - t0
                ingestion_tracker.append(current_time)
                posts_ingested_over_window = sum(
                    np.array(ingestion_tracker) > current_time - self.api_time_sleep) * self.api_date_period_limit
                if posts_ingested_over_window > self.throttling_threshold_coefficient * self.api_quarterly_posts_limit:
                    time.sleep(self.api_time_sleep * (self.api_date_period_limit / self.api_quarterly_posts_limit))

            all_publications = self.collect_posts_data(date_range)
            name = f'''radarly_{date_range[0].strftime("%Y-%m-%d-%H-%M-%S")}_{date_range[1].strftime(
                "%Y-%m-%d-%H-%M-%S")}'''

            def result_generator():
                for pub in all_publications:
                    try:
                        yield dict(pub)
                    except Exception as e:
                        ex_type, ex, tb = sys.exc_info()
                        logging.warning(f'Failed to ingest post with error: {ex}. Traceback: {traceback.print_tb(tb)}')

            yield NormalizedJSONStream(name, result_generator())

    @retry
    def collect_posts_data(self, date_range):
        param = self.get_payload(date_range[0], date_range[1])
        all_publications = self.project.get_all_publications(param)
        logging.info(f'Storing posts from {date_range[0]} to {date_range[1]}')
        return all_publications

    @staticmethod
    @retry
    def find_project(pid):
        return Project.find(pid=pid)

    def get_payload(self, start_date: datetime, end_date: datetime):
        param = Payload().creation_date(created_after=start_date, created_before=end_date) \
            .focuses(self.focus_ids) \
            .pagination(start=0, limit=self.api_request_limit)
        return param

    @retry
    def get_posts_volume(self, first_date, second_date):
        param = self.get_payload(first_date, second_date)
        posts_volume = self.project.get_all_publications(param).total
        return posts_volume

    def get_total_posts_volume(self):
        return self.get_posts_volume(first_date=self.start_date, second_date=self.end_date)

    def get_posts_volumes_from_list(self, date_ranges: List[Tuple[datetime, datetime]]) \
            -> Dict[Tuple[datetime, datetime], int]:
        """
        Outputs daily posts volumes for a given period of time
        """
        posts_volumes = OrderedDict()
        for date_range in date_ranges:
            first_date, second_date = date_range
            posts_volume = self.get_posts_volume(first_date=first_date, second_date=second_date)
            posts_volumes[date_range] = posts_volume
        return posts_volumes

    def split_date_range(self) -> Dict[Tuple[datetime, datetime], int]:
        total_count = self.get_total_posts_volume()
        logging.info(f'Posts Total Count: {total_count}')
        return self._split_date_range(self.start_date, self.end_date, posts_count=total_count)

    def _split_date_range(self, first_date, second_date, posts_count) -> Dict[Tuple[datetime, datetime], int]:
        if posts_count < self.api_date_period_limit:
            logging.debug(f'Direct Return: {[first_date, second_date]}')
            return OrderedDict({(first_date, second_date): posts_count})

        else:

            date_ranges: DateRange = self.generate_date_ranges(date_range_start=first_date,
                                                               date_range_end=second_date,
                                                               posts_count=posts_count,
                                                               extra_margin=1)
            daily_posts_volumes: Dict[Tuple[datetime, datetime], int] = date_ranges.daily_posts_volumes
            is_compliant: bool = date_ranges.is_compliant

            if is_compliant:
                res = daily_posts_volumes
            else:
                res = OrderedDict()
                for date_range, vol in daily_posts_volumes.items():
                    if vol < self.api_date_period_limit:
                        res.update({date_range: vol})
                    else:
                        res.update(self._split_date_range(*date_range, posts_count=vol))
            return res

    def generate_date_ranges(self, date_range_start, date_range_end, posts_count, extra_margin=1) -> DateRange:

        delta = (date_range_end - date_range_start)
        split_count_guess = posts_count // self.api_date_period_limit + delta.days + extra_margin
        split_range_guess = delta.total_seconds() // split_count_guess

        date_ranges_guess = self._generate_date_ranges(date_range_start, date_range_end, split_range_guess,
                                                       split_count_guess)
        daily_posts_volumes = self.get_posts_volumes_from_list(date_ranges_guess)
        is_compliant = all(np.fromiter(daily_posts_volumes.values(), dtype=int) <= 10000)

        return DateRange(daily_posts_volumes, is_compliant)

    @staticmethod
    def _generate_date_ranges(start_date, end_date, split_range, split_count):
        res = [(start_date + i * timedelta(seconds=split_range), start_date + (i + 1) * timedelta(seconds=split_range))
               for i in range(split_count - 1)]
        res += [(start_date + (split_count - 1) * timedelta(seconds=split_range), end_date)]

        return res
