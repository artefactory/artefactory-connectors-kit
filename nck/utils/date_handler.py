import calendar
from datetime import date, timedelta
from typing import Tuple


def get_date_start_and_date_stop_from_range(
    date_range: str
) -> Tuple[date, date]:
    today = date.today()
    if date_range == "PREVIOUS_MONTH":
        last_day_of_previous_month = \
            today.replace(day=1) - timedelta(days=1)
        year = last_day_of_previous_month.year
        month = last_day_of_previous_month.month
        return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])
    elif date_range == "PREVIOUS_WEEK":
        # The API uses American standard, weeks go from sunday yo next saturday
        first_day_of_last_week = today - timedelta(days=today.weekday() + 1, weeks=1)
        return first_day_of_last_week, first_day_of_last_week + timedelta(days=6)
    else:
        return None
