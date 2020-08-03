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

from twitter_ads.campaign import FundingInstrument, Campaign, LineItem
from twitter_ads.creative import MediaCreative, PromotedTweet, CardsFetch


REPORT_TYPES = ["ANALYTICS", "REACH", "ENTITY"]

ENTITY_OBJECTS = {
    "FUNDING_INSTRUMENT": FundingInstrument,
    "CAMPAIGN": Campaign,
    "LINE_ITEM": LineItem,
    "MEDIA_CREATIVE": MediaCreative,
    "PROMOTED_TWEET": PromotedTweet,
}

ENTITY_ATTRIBUTES = {
    **{
        entity: list(ENTITY_OBJECTS[entity].__dict__["PROPERTIES"].keys())
        for entity in ENTITY_OBJECTS
    },
    "CARD": list(CardsFetch.__dict__["PROPERTIES"].keys()),
}

GRANULARITIES = ["DAY", "TOTAL"]

METRIC_GROUPS = [
    "ENGAGEMENT",
    "BILLING",
    "VIDEO",
    "MEDIA",
    "MOBILE_CONVERSION",
    "WEB_CONVERSION",
    "LIFE_TIME_VALUE_MOBILE_CONVERSION",
]

PLACEMENTS = [
    "ALL_ON_TWITTER",
    "PUBLISHER_NETWORK",
]

SEGMENTATION_TYPES = [
    "AGE",
    "APP_STORE_CATEGORY",
    "AUDIENCES",
    "CONVERSATIONS",
    "CONVERSION_TAGS",
    "DEVICES",
    "EVENTS",
    "GENDER",
    "INTERESTS",
    "KEYWORDS",
    "LANGUAGES",
    "LOCATIONS",
    "METROS",
    "PLATFORMS",
    "PLATFORM_VERSIONS",
    "POSTAL_CODES",
    "REGIONS",
    "SIMILAR_TO_FOLLOWERS_OF_USER",
    "TV_SHOWS",
]
