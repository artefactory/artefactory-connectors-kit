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

from functools import update_wrapper

from ack.config import logger


def processor(*sensitive_fields):
    """Helper decorator to rewrite a function so that it returns another
    function from it.
    """

    def wrapper(f):
        def new_func(*args, **kwargs):

            _kwargs = {}

            for key, value in kwargs.items():
                if key in sensitive_fields:
                    _kwargs[key] = "*****"
                else:
                    _kwargs[key] = value

            logger.info(f"Calling {f.__name__} with ({_kwargs})")

            def processor():
                return f(*args, **kwargs)

            return update_wrapper(processor, f)

        return update_wrapper(new_func, f)

    return wrapper
