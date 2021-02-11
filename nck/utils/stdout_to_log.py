import logging
import sys


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


def StdoutToLog(logger_name, level):
    def StdoutToLogDec(func):
        def wrapper(*args, **kwargs):
            httpLog = STDoutToLog(logger_name, level)
            sys.stdout = httpLog
            func(*args, **kwargs)
            sys.stdout = sys.__stdout__

        return wrapper

    return StdoutToLogDec
