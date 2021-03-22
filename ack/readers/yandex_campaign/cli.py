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
from ack.readers.yandex_campaign.config import CAMPAIGN_FIELDS, CAMPAIGN_PAYMENT_STATUSES, CAMPAIGN_STATES, CAMPAIGN_STATUSES
from ack.readers.yandex_campaign.reader import YandexCampaignReader
from ack.utils.args import extract_args
from ack.utils.processor import processor


@click.command(name="read_yandex_campaigns")
@click.option("--yandex-campaigns-token", "yandex_token", required=True)
@click.option("--yandex-campaigns-campaign-id", "yandex_campaign_ids", multiple=True)
@click.option("--yandex-campaigns-campaign-state", "yandex_campaign_states", multiple=True, type=click.Choice(CAMPAIGN_STATES))
@click.option(
    "--yandex-campaigns-campaign-status", "yandex_campaign_statuses", multiple=True, type=click.Choice(CAMPAIGN_STATUSES)
)
@click.option(
    "--yandex-campaigns-campaign-payment-status",
    "yandex_campaign_payment_statuses",
    multiple=True,
    type=click.Choice(CAMPAIGN_PAYMENT_STATUSES),
)
@click.option(
    "--yandex-campaigns-field-name",
    "yandex_fields",
    multiple=True,
    type=click.Choice(CAMPAIGN_FIELDS),
    required=True,
    help=(
        "Fields to output in the report (columns)."
        "For the full list of fields and their meanings, "
        "see https://tech.yandex.com/direct/doc/reports/fields-list-docpage/"
    ),
)
@processor("yandex_token")
def yandex_campaigns(**kwargs):
    return YandexCampaignReader(**extract_args("yandex_", kwargs))
