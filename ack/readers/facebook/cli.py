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

import click
from click import ClickException
from ack.readers.facebook.config import ACTION_BREAKDOWNS, BREAKDOWNS, DATE_PRESETS, FACEBOOK_OBJECTS
from ack.readers.facebook.reader import FacebookReader
from ack.utils.args import extract_args
from ack.utils.processor import processor


def check_object_id(ctx, param, values):
    try:
        [int(value) for value in values]
        return values
    except ValueError:
        raise ClickException("Wrong format. Ad object IDs should only contains digits.")


@click.command(name="read_facebook")
@click.option("--facebook-app-id", default="", help="Not mandatory for AdsInsights reporting if access-token provided")
@click.option("--facebook-app-secret", default="", help="Not mandatory for AdsInsights reporting if access-token provided")
@click.option("--facebook-access-token", required=True)
@click.option("--facebook-object-id", required=True, multiple=True, callback=check_object_id)
@click.option("--facebook-object-type", type=click.Choice(FACEBOOK_OBJECTS), default="account")
@click.option("--facebook-level", type=click.Choice(FACEBOOK_OBJECTS), default="ad", help="Granularity of result")
@click.option(
    "--facebook-ad-insights",
    type=click.BOOL,
    default=True,
    help="https://developers.facebook.com/docs/marketing-api/insights",
)
@click.option(
    "--facebook-breakdown",
    multiple=True,
    type=click.Choice(BREAKDOWNS),
    help="https://developers.facebook.com/docs/marketing-api/insights/breakdowns/",
)
@click.option(
    "--facebook-action-breakdown",
    multiple=True,
    type=click.Choice(ACTION_BREAKDOWNS),
    help="https://developers.facebook.com/docs/marketing-api/insights/breakdowns#actionsbreakdown",
)
@click.option("--facebook-field", multiple=True, help="API fields, following Artefact format")
@click.option("--facebook-time-increment")
@click.option("--facebook-start-date", type=click.DateTime())
@click.option("--facebook-end-date", type=click.DateTime())
@click.option("--facebook-date-preset", type=click.Choice(DATE_PRESETS))
@click.option(
    "--facebook-add-date-to-report",
    type=click.BOOL,
    default=False,
    help="If set to true, the date of the request will appear in the report",
)
@processor("facebook_app_secret", "facebook_access_token")
def facebook(**kwargs):
    return FacebookReader(**extract_args("facebook_", kwargs))
