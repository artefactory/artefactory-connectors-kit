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

from datetime import datetime


def add_metric_container_to_report_description(rep_desc, dimensions, metrics, breakdown_item_ids):
    """
    Filling the metricContainer section of a report description:
    - Creates 1 filter per dimension breakdown x metric
    - Applies filters to each metric
    """

    nb_breakdowns = len(breakdown_item_ids)
    nb_metrics = len(metrics)

    rep_desc["metricContainer"]["metricFilters"] = [
        {
            "id": i + j * nb_breakdowns,
            "type": "breakdown",
            "dimension": f"variables/{dimensions[i]}",
            "itemId": breakdown_item_ids[i],
        }
        for j in range(nb_metrics)
        for i in range(nb_breakdowns)
    ]

    rep_desc["metricContainer"]["metrics"] = [
        {"id": f"metrics/{metrics[j]}", "filters": [i + j * nb_breakdowns for i in range(nb_breakdowns)]}
        for j in range(nb_metrics)
    ]

    return rep_desc


def get_node_values_from_response(response):
    """
    Extracting dimension values from a report response,
    and returning them into a dictionnary of nodes: {name_itemId: value}
    For instance: {'daterangeday_1200201': 'Mar 1, 2020'}
    """

    name = response["columns"]["dimension"]["id"].split("/")[1]
    values = [row["value"] for row in response["rows"]]
    item_ids = [row["itemId"] for row in response["rows"]]

    return {f"{name}_{item_id}": value for (item_id, value) in zip(item_ids, values)}


def get_item_ids_from_nodes(list_of_strings):
    """
    Extacting item_ids from a list of nodes,
    each node being expressed as 'name_itemId'
    """

    return [string.split("_")[1] for string in list_of_strings if string]


def format_date(date_string):
    """
    Input: "Jan 1, 2020"
    Output: "2020-01-01"
    """
    return datetime.strptime(date_string, "%b %d, %Y").strftime("%Y-%m-%d")


def parse_response(response, metrics, parent_dim_parsed):
    """
    Parsing a raw JSON response into the following format:
    {dimension: value, metric: value} (1 dictionnary per row)
    """

    dimension = response["columns"]["dimension"]["id"].split("variables/")[1]

    for row in response["rows"]:
        parsed_row_metrics = {m: v for m, v in zip(metrics, row["data"])}
        parsed_row = {
            **parent_dim_parsed,
            dimension: row["value"],
            **parsed_row_metrics,
        }
        parsed_row = {k: (format_date(v) if k == "daterangeday" else v) for k, v in parsed_row.items()}
        yield parsed_row
