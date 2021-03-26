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
from ack.readers.salesforce.reader import SalesforceReader
from ack.utils.args import extract_args, has_arg, hasnt_arg
from ack.utils.processor import processor


@click.command(name="read_salesforce")
@click.option("--salesforce-consumer-key", required=True)
@click.option("--salesforce-consumer-secret", required=True)
@click.option("--salesforce-user", required=True)
@click.option("--salesforce-password", required=True)
@click.option("--salesforce-object-type")
@click.option("--salesforce-query")
@click.option("--salesforce-query-name")
@click.option("--salesforce-watermark-column")
@click.option("--salesforce-watermark-init")
@click.option("--salesforce-redis-state-service-name")
@click.option("--salesforce-redis-state-service-host")
@click.option("--salesforce-redis-state-service-port", default=6379)
@processor("salesforce_consumer_key", "salesforce_consumer_secret", "salesforce_password")
def salesforce(**kwargs):
    query_key = "salesforce_query"
    query_name_key = "salesforce_query_name"
    object_type_key = "salesforce_object_type"
    watermark_column_key = "salesforce_watermark_column"
    watermark_init_key = "salesforce_watermark_init"
    redis_state_service_keys = [
        "salesforce_redis_state_service_name",
        "salesforce_redis_state_service_host",
        "salesforce_redis_state_service_port",
    ]

    if hasnt_arg(query_key, kwargs) and hasnt_arg(object_type_key, kwargs):
        raise click.BadParameter("Must specify either an object type or a query for Salesforce")

    if has_arg(query_key, kwargs) and has_arg(object_type_key, kwargs):
        raise click.BadParameter("Cannot specify both a query and an object type for Salesforce")

    if has_arg(query_key, kwargs) and hasnt_arg(query_name_key, kwargs):
        raise click.BadParameter("Must specify a query name when running a Salesforce query")

    redis_state_service_enabled = all([has_arg(key, kwargs) for key in redis_state_service_keys])

    if has_arg(watermark_column_key, kwargs) and not redis_state_service_enabled:
        raise click.BadParameter("You must configure state management to use Salesforce watermarks")

    if hasnt_arg(watermark_column_key, kwargs) and redis_state_service_enabled:
        raise click.BadParameter("You must specify a Salesforce watermark when using state management")

    if hasnt_arg(watermark_init_key, kwargs) and redis_state_service_enabled:
        raise click.BadParameter("You must specify an initial Salesforce watermark value when using state management")

    return SalesforceReader(**extract_args("salesforce_", kwargs))
