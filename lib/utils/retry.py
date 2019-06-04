from tenacity import retry as _retry, wait_exponential, before_sleep_log, before_log
import config
import logging


def retry(fn):

    return _retry(wait=wait_exponential(multiplier=1, min=4, max=10),
                  reraise=True,
                  before=before_log(config.logger, logging.DEBUG),
                  before_sleep=before_sleep_log(config.logger, logging.DEBUG))(fn)
