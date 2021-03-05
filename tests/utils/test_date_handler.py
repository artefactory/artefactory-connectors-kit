import unittest
from datetime import date

from freezegun import freeze_time
from nck.utils.date_handler import (
    check_date_range_definition_conformity,
    get_date_start_and_date_stop_from_date_range,
    build_date_range,
)
from nck.utils.exceptions import DateDefinitionException
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

    @parameterized.expand(
        [
            (None, date(2021, 1, 12), None),
            (None, date(2021, 1, 12), "YESTERDAY"),
            (date(2021, 1, 12), None, None),
            (date(2021, 1, 12), None, "YESTERDAY"),
        ]
    )
    def test_check_date_range_definition_conformity_if_missing_date(self, start_date, end_date, date_range):
        with self.assertRaises(DateDefinitionException):
            check_date_range_definition_conformity(start_date, end_date, date_range)

    def test_check_date_range_definition_conformity_if_no_date(self):
        with self.assertRaises(DateDefinitionException):
            check_date_range_definition_conformity(None, None, None)

    def test_check_date_range_definition_conformity_if_inconsistent(self):
        with self.assertRaises(DateDefinitionException):
            check_date_range_definition_conformity(date(2021, 1, 12), date(2021, 1, 31), "YESTERDAY")

    @parameterized.expand([(date(2021, 1, 12), date(2021, 1, 31), None), (None, None, "YESTERDAY")])
    def test_check_date_range_definition_conformity(self, start_date, end_date, date_range):
        self.assertIsNone(check_date_range_definition_conformity(start_date, end_date, date_range))

    @freeze_time("2021-02-11")
    def test_build_date_range_without_dates(self):
        self.assertTupleEqual(build_date_range(None, None, "PREVIOUS_MONTH"), (date(2021, 1, 1), date(2021, 1, 31)))

    def test_build_date_range_with_dates(self):
        self.assertTupleEqual(
            build_date_range(date(2021, 1, 1), date(2021, 1, 31), None), (date(2021, 1, 1), date(2021, 1, 31))
        )
