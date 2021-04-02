from datetime import datetime
from typing import List

from pydantic import BaseModel, validator


class RadarlyReaderConfig(BaseModel):
    pid: int
    client_id: str
    client_secret: str
    focus_id: List[int]
    start_date: datetime = None
    end_date: datetime = None
    api_request_limit: int = 250
    api_date_period_limit: int = int(1e4)
    api_quarterly_posts_limit: int = int(45e3)
    api_window: int = 300
    throttle: bool = True
    throttling_threshold_coefficient: float = 0.95

    @validator("start_date", "end_date", pre=True)
    def date_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Datetime format must follow 'YYYY-MM-DD'")
        return v
