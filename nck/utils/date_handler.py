import calendar
from datetime import date, timedelta
from typing import Tuple


def get_date_start_and_date_stop_from_date_range(date_range: str) -> Tuple[date, date]:
    current_date = date.today()
    if date_range == "YESTERDAY":
        return __get_yesterday_date(current_date)
    elif date_range == "LAST_7_DAYS":
        return __get_last_7d_dates(current_date)
    elif date_range == "LAST_90_DAYS":
        return __get_last_90d_dates(current_date)
    elif date_range == "PREVIOUS_WEEK":
        return __get_previous_week_dates(current_date)
    elif date_range == "PREVIOUS_MONTH":
        return __get_previous_month_dates(current_date)


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
