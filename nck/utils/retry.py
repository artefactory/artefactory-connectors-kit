from tenacity import (
    retry as _retry,
    wait_exponential,
    before_sleep_log,
    before_log,
    stop_after_attempt,
)
import config
import logging


def retry(fn):
    return _retry(
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(5),
        reraise=True,
        before=before_log(config.logger, logging.INFO),
        before_sleep=before_sleep_log(config.logger, logging.INFO),
    )(fn)
