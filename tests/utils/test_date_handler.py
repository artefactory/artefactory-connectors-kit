from datetime import date
import unittest
from unittest.mock import patch

from parameterized import parameterized

from nck.utils.date_handler import get_date_start_and_date_stop_from_range


class TestDateHandler(unittest.TestCase):

    @parameterized.expand([
        (
            date(2020, 2, 1),
            (date(2020, 1, 1), date(2020, 1, 31))
        ),
        (
            date(2020, 1, 1),
            (date(2019, 12, 1), date(2019, 12, 31))
        ),
        (
            date(2020, 2, 15),
            (date(2020, 1, 1), date(2020, 1, 31))
        ),
        (
            date(2019, 12, 1),
            (date(2019, 11, 1), date(2019, 11, 30))
        )
    ])
    def test_get_date_start_and_date_stop_with_previous_month(self, date_of_day, expected):
        input_range = "PREVIOUS_MONTH"
        with patch("nck.utils.date_handler.date") as mock_date:
            mock_date.today.return_value = date_of_day
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            self.assertTupleEqual(
                expected,
                get_date_start_and_date_stop_from_range(input_range),
                f"Bad return when freezed date is {date_of_day}"
            )

    @parameterized.expand([
        (
            date(2020, 1, 6),
            (date(2019, 12, 30), date(2020, 1, 5))
        ),
        (
            date(2020, 1, 13),
            (date(2020, 1, 6), date(2020, 1, 12))
        )
    ])
    def test_get_date_start_and_date_stop_with_previous_week(self, date_of_day, expected):
        input_range = "PREVIOUS_WEEK"
        with patch("nck.utils.date_handler.date") as mock_date:
            mock_date.today.return_value = date_of_day
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            self.assertTupleEqual(
                expected,
                get_date_start_and_date_stop_from_range(input_range),
                f"Bad return when freezed date is {date_of_day}"
            )
