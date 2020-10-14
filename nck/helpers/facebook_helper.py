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
import json
from time import sleep

from facebook_business.adobjects.adsinsights import AdsInsights

FACEBOOK_OBJECTS = ["creative", "ad", "adset", "campaign", "account"]

DATE_PRESETS = [
    v for k, v in AdsInsights.DatePreset.__dict__.items() if not k.startswith("__")
]

BREAKDOWNS = [
    v for k, v in AdsInsights.Breakdowns.__dict__.items() if not k.startswith("__")
]

ACTION_BREAKDOWNS = [
    v
    for k, v in AdsInsights.ActionBreakdowns.__dict__.items()
    if not k.startswith("__")
]


def get_action_breakdown_filters(field_path):
    """
    Extracts action breakdown filters from a field path,
    and returns them as a dictionnary.

    For instance:
        'actions[action_type:video_view][action_type:post_engagement][action_device:iphone]'
    returns:
        {'action_type':['video_view','post_engagement'],
        'action_device':['iphone']}
    """
    filters = {}
    for path_item in field_path:
        if ":" in path_item:
            action_breakdown, action_breakdown_value = path_item.split(":")
            filters.setdefault(action_breakdown, []).append(action_breakdown_value)
    return filters


def format_field_path(field_path):
    """
    Formats a field_path back into a field.

    For instance:
        ['actions', 'action_type:post_engagement']
    returns:
        'actions[action_type:post_engagement]'
    """
    if len(field_path) == 1:
        return field_path[0]
    else:
        return "".join([field_path[0]] + [f"[{element}]" for element in field_path[1:]])


def check_if_obj_meets_action_breakdown_filters(obj, filters):
    """
    Checks if a nested action breakdown object
    meets the conditions defined by action breakdown filters.

    For instance, if action breakdown filters are:
        {'action_type': ['post_engagement', 'video_view']
        'action_device': ['iphone']}
    Outputs will be:
    - {'action_type':'post_engagement', 'action_device':'iphone', 'value':12}: True
    - {'action_type':'video_view', 'action_device':'iphone', 'value':12}: True
    - {'action_type':'post_engagement', 'action_device':'desktop', 'value':12}: False
    """
    for action_breakdown in filters:
        if obj[action_breakdown] not in filters[action_breakdown]:
            return False
    return True


def get_action_breakdown_value(obj, visited, action_breakdowns):
    """
    Extracts the action breakdown value
    of a nested action breakdown object.

    For instance:
        {actions: [{'action_type':'video_view', 'action_device':'iphone', 'value':'12'}]}
        Here, the nested action_breakdown object is:
            {'action_type':'video_view', 'action_device':'iphone', 'value':'12'}
    returns:
        {'actions[action_type:video_view][action_device:iphone]': '12'}
    """
    obj_action_breakdown = [
        f"{action_breakdown}:{obj[action_breakdown]}"
        for action_breakdown in action_breakdowns
        if action_breakdown in obj
    ]
    return {format_field_path(visited + obj_action_breakdown): obj["value"]}


def get_all_action_breakdown_values(resp_obj, visited, action_breakdowns, filters={}):
    """
    Extracts action breakdown values from a list of nested action breakdown objects,
    only if they meet the conditions defined by action breakdown filters.
    """
    action_breakdown_values = {}
    for obj in resp_obj:
        if filters != {}:
            if check_if_obj_meets_action_breakdown_filters(obj, filters):
                action_breakdown_values.update(
                    get_action_breakdown_value(obj, visited, action_breakdowns)
                )
        else:
            action_breakdown_values.update(
                get_action_breakdown_value(obj, visited, action_breakdowns)
            )
    return action_breakdown_values


def get_field_values(resp_obj, field_path, action_breakdowns, visited=[]):
    """
    Recursive function extracting (and formating) the values
    of a requested field from an API response and a field path.
    """
    path_item = field_path[0]
    remaining_path_items = len(field_path) - 1

    visited.append(path_item)

    if path_item in resp_obj:
        current_obj = resp_obj[path_item]
        if remaining_path_items == 0:
            if (
                isinstance(current_obj, list)
                and all(isinstance(elt, str) for elt in current_obj)
            ):
                return {format_field_path(visited): "|".join(map(str, current_obj))}
            elif (
                isinstance(current_obj, list)
                and all(isinstance(elt, dict) for elt in current_obj)
                and all(any(key.startswith("action_") for key in elt.keys()) for elt in current_obj)
            ):
                return get_all_action_breakdown_values(current_obj, visited, action_breakdowns)
            else:
                # For exploration purposes
                return {format_field_path(visited): str(current_obj)}
        else:
            return get_field_values(current_obj, field_path[1:], action_breakdowns, visited)
    else:
        if all(":" in f for f in field_path):
            filters = get_action_breakdown_filters(field_path)
            return get_all_action_breakdown_values(resp_obj, visited[:-1], action_breakdowns, filters)


def generate_batches(iterable, batch_size):
    """
    Yields lists of length size batch_size,
    containing objects yielded by the iterable.
    """

    batch = []
    for obj in iterable:
        if len(batch) == batch_size:
            yield batch
            batch = []
        batch.append(obj)

    if len(batch):
        yield batch


def monitor_usage(response):
    """
    Extracts "X-Business-Use-Case-Usage" header from a FacebookResponse object.
    If one of the 3 API usage rates (call_count, total_cputime, total_time)
    is above 75%, puts the program to sleep for 5 minutes.
    Documentation: https://developers.facebook.com/docs/graph-api/overview/rate-limiting/
    """

    for header in response._headers:
        if header["name"] == "X-Business-Use-Case-Usage":
            usage_header = json.loads(header["value"])
            usage_header_values = list(usage_header.values())[0][0]
            usage_rates = [
                v
                for k, v in usage_header_values.items()
                if k in ["call_count", "total_cputime", "total_time"]
            ]

    if max(usage_rates) > 75:
        logging.info("75% rate limit reached. Sleeping for 5 minutes...")
        sleep(300)
