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

from datetime import datetime

from nck.config import logger
from nck.readers.the_trade_desk.config import API_DATEFORMAT, BQ_DATEFORMAT


class ReportTemplateNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)
        logger.error(message)


class ReportScheduleNotReadyError(Exception):
    def __init__(self, message):
        super().__init__(message)
        logger.error(message)


def format_date(date_string):
    """
    Input: "2020-01-01T00:00:00"
    Output: "2020-01-01"
    """
    return datetime.strptime(date_string, API_DATEFORMAT).strftime(BQ_DATEFORMAT)
