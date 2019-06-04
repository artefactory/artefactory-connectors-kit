from tenacity import retry as _retry, wait_exponential, before_sleep_log, before_log
from functools import update_wrapper
import config
import logging


def retry(fn):
        @_retry(wait=wait_exponential(multiplier=1, min=4, max=10),
                reraise=True,
                before=before_log(config.logger, logging.INFO),
                before_sleep=before_sleep_log(config.logger, logging.INFO))
        def retry_wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return update_wrapper(retry_wrapper, fn)
