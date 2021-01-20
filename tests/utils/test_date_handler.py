import unittest
from datetime import date

from freezegun import freeze_time
from nck.utils.date_handler import get_date_start_and_date_stop_from_date_range
from parameterized import parameterized


class TestDateHandler(unittest.TestCase):
    @parameterized.expand(
        [
            ("YESTERDAY", (date(2021, 1, 12), date(2021, 1, 12))),
            ("LAST_7_DAYS", (date(2021, 1, 5), date(2021, 1, 12))),
            ("LAST_90_DAYS", (date(2020, 10, 14), date(2021, 1, 12))),
        ]
    )
    @freeze_time("2021-01-13")
    def test_get_date_start_and_date_stop_from_date_range(self, date_range, expected):
        self.assertTupleEqual(get_date_start_and_date_stop_from_date_range(date_range), expected)

    @freeze_time("2021-01-11")
    def test_get_previous_week_dates_if_monday(self):
        self.assertTupleEqual(
            get_date_start_and_date_stop_from_date_range("PREVIOUS_WEEK"), (date(2021, 1, 4), date(2021, 1, 10))
        )

    @freeze_time("2021-01-13")
    def test_get_previous_week_dates_if_midweek(self):
        self.assertTupleEqual(
            get_date_start_and_date_stop_from_date_range("PREVIOUS_WEEK"), (date(2021, 1, 4), date(2021, 1, 10))
        )

    @freeze_time("2021-01-17")
    def test_get_previous_week_dates_if_sunday(self):
        self.assertTupleEqual(
            get_date_start_and_date_stop_from_date_range("PREVIOUS_WEEK"), (date(2021, 1, 4), date(2021, 1, 10))
        )

    @freeze_time("2021-01-11")
    def test_get_previous_month_dates_if_first_month_of_the_year(self):
        self.assertTupleEqual(
            get_date_start_and_date_stop_from_date_range("PREVIOUS_MONTH"), (date(2020, 12, 1), date(2020, 12, 31))
        )

    @freeze_time("2021-02-11")
    def test_get_previous_month_dates_if_random_month_of_the_year(self):
        self.assertTupleEqual(
            get_date_start_and_date_stop_from_date_range("PREVIOUS_MONTH"), (date(2021, 1, 1), date(2021, 1, 31))
        )
