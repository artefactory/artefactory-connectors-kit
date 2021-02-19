import logging
import sys
import httplib2


class STDoutToLog:
    def __init__(self, logger_name, level):
        self.content = []
        self.logg = logging.getLogger(logger_name)
        self.level = level

    def write(self, string):
        if not string.endswith("\n"):
            self.content.append(string)
        else:
            debug_info = (
                "".join(self.content)
                .replace("\\r", "")
                .encode("latin1")
                .decode("unicode-escape")
                .encode("latin1")
                .decode("utf-8")
                .replace("'", "")
            )

            debug_info = "\n".join([ll.rstrip() for ll in debug_info.splitlines() if ll.strip()])
            self.logg.log(self.level, debug_info)
            self.content = []

    def flush(self):
        pass


def http_log(logger_name, level=logging.DEBUG):
    def decorator(func):
        def wrapper(*args, **kwargs):
            httplib2.debuglevel = 4

            httpLog = STDoutToLog(logger_name, level)
            sys.stdout = httpLog

            items = []
            for item in func(*args, **kwargs):
                items.append(item)

            sys.stdout = sys.__stdout__

            for item in items:
                yield item

        return wrapper

    return decorator


def http_log_for_init(logger_name, level=logging.DEBUG):
    def decorator(func):
        def wrapper(*args, **kwargs):
            httplib2.debuglevel = 4

            httpLog = STDoutToLog(logger_name, level)
            sys.stdout = httpLog
            func(*args, **kwargs)
            sys.stdout = sys.__stdout__

        return wrapper

    return decorator
