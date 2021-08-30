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


class RetryTimeoutError(Exception):
    """Raised when a query exceeds it's time limit threshold."""

    pass


class SdfOperationError(Exception):
    """Raised when a sdf operation has failed."""

    pass


class DateDefinitionException(Exception):
    """Raised when the date parameters are not valid"""

    pass


class NoDateDefinitionException(Exception):
    """Raised when no date range or start date/end date is defined"""

    pass


class MissingDateDefinitionException(Exception):
    """Raised when either the start date or end date is missing"""

    pass


class InconsistentDateDefinitionException(Exception):
    """Raised when both start date/end date and date range are defined"""

    pass


class MissingItemsInResponse(Exception):
    """Raised when the body of the response is missing items"""

    pass


class APIRateLimitError(Exception):
    """Raised when the API rate limit is reached"""

    pass


class ReportDescriptionError(Exception):
    """Raised when report description is not valid"""

    pass


class ReportNotReadyError(Exception):
    """Raised when report is not ready yet"""

    pass


class ReportTemplateNotFoundError(Exception):
    """Raised when The Trade Desk report template was not found"""

    pass


class ReportScheduleNotReadyError(Exception):
    """Raised when The Trade Desk report schedule is not ready yet"""

    pass


class FilterNotFoundError(Exception):
    """Raised when a dimension filter is not found"""

    pass


class RateLimitExceeded(Exception):
    """Raised when the requests-per-time unit limit was exceeded"""

    pass
