import calendar
from datetime import date, timedelta, datetime
from typing import Tuple

from nck.utils.exceptions import DateDefinitionException


def __get_yesterday_date(current_date: date) -> Tuple[date, date]:
    yesterday = current_date - timedelta(days=1)
    return yesterday, yesterday


def __get_last_7d_dates(current_date: date) -> Tuple[date, date]:
    return current_date - timedelta(days=8), current_date - timedelta(days=1)


def __get_last_90d_dates(current_date: date) -> Tuple[date, date]:
    return current_date - timedelta(days=91), current_date - timedelta(days=1)


def __get_previous_week_dates(current_date: date) -> Tuple[date, date]:
    first_day_of_last_week = current_date - timedelta(days=current_date.weekday(), weeks=1)
    return first_day_of_last_week, first_day_of_last_week + timedelta(days=6)


def __get_previous_month_dates(current_date: date) -> Tuple[date, date]:
    last_day_of_previous_month = current_date.replace(day=1) - timedelta(days=1)
    year = last_day_of_previous_month.year
    month = last_day_of_previous_month.month
    return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])


DEFAULT_DATE_RANGE_FUNCTIONS = {
    "YESTERDAY": __get_yesterday_date,
    "LAST_7_DAYS": __get_last_7d_dates,
    "PREVIOUS_WEEK": __get_previous_week_dates,
    "PREVIOUS_MONTH": __get_previous_month_dates,
    "LAST_90_DAYS": __get_last_90d_dates,
}


def check_date_range_definition_conformity(start_date: date, end_date: date, date_range: str):

    if date_range:
        if any([start_date, end_date]):
            raise DateDefinitionException("You must define either (start_date, end_date) or date_range")
    else:
        if not all([start_date, end_date]):
            raise DateDefinitionException("You must at least define a couple (start-date, end-date) or a date-range")
        elif end_date < start_date:
            raise DateDefinitionException("Report end date should be equal or ulterior to report start date.")


def get_date_start_and_date_stop_from_date_range(date_range: str) -> Tuple[date, date]:
    """Returns date start and date stop based on the date range provided
    and the current date.

    Args:
        date_range (str): One of the default date ranges that exist

    Returns:
        Tuple[date, date]: date start and date stop that match the date range
    """
    current_date = date.today()
    return DEFAULT_DATE_RANGE_FUNCTIONS[date_range](current_date)


def build_date_range(start_date, end_date, date_range):
    """Returns date start and date end adapted if there is a date range.

    Args:
        start_date (date): start date
        end_date (date): end date
        date_range (str): One of the default date ranges that exist

    Returns:
        Tuple[datetime, datetime]: date start and date stop that match the date range
    """
    check_date_range_definition_conformity(start_date, end_date, date_range)

    if date_range is not None:
        start_date, end_date = get_date_start_and_date_stop_from_date_range(date_range)
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.min.time())

    return start_date, end_date
