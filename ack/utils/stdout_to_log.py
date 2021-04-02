# GNU Lesser General Public License v3.0 only
# Copyright (C) 2020 Artefact
# licence-information@artefact.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

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
