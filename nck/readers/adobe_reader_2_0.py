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
import click
import json
import requests
import time
from itertools import chain
from datetime import timedelta

from nck.utils.retry import retry
from nck.utils.args import extract_args
from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.clients.adobe_client import AdobeClient
from nck.streams.json_stream import JSONStream
from nck.helpers.adobe_helper_2_0 import (
    APIRateLimitError,
    add_metric_container_to_report_description,
    get_node_values_from_response,
    get_item_ids_from_nodes,
    parse_response,
)

DATEFORMAT = "%Y-%m-%dT%H:%M:%S"
API_WINDOW_DURATION = 6
API_REQUESTS_OVER_WINDOW_LIMIT = 12


def format_key_if_needed(ctx, param, value):
    """
    In some cases, newlines are escaped when passed as a click.option().
    This callback corrects this unexpected behaviour.
    """
    return value.replace("\\n", "\n")


@click.command(name="read_adobe_2_0")
@click.option(
    "--adobe-2-0-client-id",
    required=True,
    help="Client ID, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-2-0-client-secret",
    required=True,
    help="Client Secret, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-2-0-tech-account-id",
    required=True,
    help="Technical Account ID, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-2-0-org-id",
    required=True,
    help="Organization ID, that you can find in your integration section on Adobe Developper Console.",
)
@click.option(
    "--adobe-2-0-private-key",
    required=True,
    callback=format_key_if_needed,
    help="Content of the private.key file, that you had to provide to create the integration. "
    "Make sure to enter the parameter in quotes, include headers, and indicate newlines as '\\n'.",
)
@click.option(
    "--adobe-2-0-global-company-id",
    required=True,
    help="Global Company ID, to be requested to Discovery API. "
    "Doc: https://www.adobe.io/apis/experiencecloud/analytics/docs.html#!AdobeDocs/analytics-2.0-apis/master/discovery.md)",
)
@click.option(
    "--adobe-2-0-report-suite-id",
    required=True,
    help="ID of the requested Adobe Report Suite",
)
@click.option(
    "--adobe-2-0-dimension",
    required=True,
    multiple=True,
    help="To get dimension names, enable the Debugger feature in Adobe Analytics Workspace: "
    "it will allow you to visualize the back-end JSON requests made by Adobe Analytics UI to Reporting API 2.0. "
    "Doc: https://github.com/AdobeDocs/analytics-2.0-apis/blob/master/reporting-tricks.md",
)
@click.option(
    "--adobe-2-0-metric",
    required=True,
    multiple=True,
    help="To get metric names, enable the Debugger feature in Adobe Analytics Workspace: "
    "it will allow you to visualize the back-end JSON requests made by Adobe Analytics UI to Reporting API 2.0. "
    "Doc: https://github.com/AdobeDocs/analytics-2.0-apis/blob/master/reporting-tricks.md",
)
@click.option(
    "--adobe-2-0-start-date",
    required=True,
    type=click.DateTime(),
    help="Start date of the report",
)
@click.option(
    "--adobe-2-0-end-date",
    required=True,
    type=click.DateTime(),
    help="End date of the report",
)
@processor(
    "adobe_2_0_client_id",
    "adobe_2_0_client_secret",
    "adobe_2_0_tech_account_id",
    "adobe_2_0_org_id",
    "adobe_2_0_private_key",
)
def adobe_2_0(**kwargs):
    return AdobeReader_2_0(**extract_args("adobe_2_0_", kwargs))


class AdobeReader_2_0(Reader):
    def __init__(
        self,
        client_id,
        client_secret,
        tech_account_id,
        org_id,
        private_key,
        global_company_id,
        report_suite_id,
        dimension,
        metric,
        start_date,
        end_date,
    ):
        self.adobe_client = AdobeClient(
            client_id, client_secret, tech_account_id, org_id, private_key
        )
        self.global_company_id = global_company_id
        self.report_suite_id = report_suite_id
        self.dimensions = list(dimension)
        self.metrics = list(metric)
        self.start_date = start_date
        self.end_date = end_date + timedelta(days=1)
        self.ingestion_tracker = []
        self.node_values = {}

    def build_date_range(self):
        return f"{self.start_date.strftime(DATEFORMAT)}/{self.end_date.strftime(DATEFORMAT)}"

    def build_report_description(self, metrics, breakdown_item_ids=[]):
        """
        Building a report description, to be passed as a parameter to the Reporting API.
        Documentation:
        - https://github.com/AdobeDocs/analytics-2.0-apis/blob/master/reporting-multiple-breakdowns.md
        - https://github.com/AdobeDocs/analytics-2.0-apis/blob/master/reporting-tricks.md
        """

        rep_desc = {
            "rsid": self.report_suite_id,
            "globalFilters": [
                {"type": "dateRange", "dateRange": self.build_date_range()}
            ],
            "metricContainer": {},
            "dimension": f"variables/{self.dimensions[len(breakdown_item_ids)]}",
            "settings": {"countRepeatInstances": "true", "limit": "5000"},
        }

        rep_desc = add_metric_container_to_report_description(
            rep_desc=rep_desc,
            dimensions=self.dimensions,
            metrics=metrics,
            breakdown_item_ids=breakdown_item_ids,
        )

        return rep_desc

    def throttle(self):
        """
        Monitoring API rate limit (12 requests every 6 seconds).
        """

        current_time = time.time()
        self.ingestion_tracker.append(current_time)
        window_ingestion_tracker = [
            t
            for t in self.ingestion_tracker
            if t >= (current_time - API_WINDOW_DURATION)
        ]

        if len(window_ingestion_tracker) >= API_REQUESTS_OVER_WINDOW_LIMIT:
            sleep_time = (
                window_ingestion_tracker[0] + API_WINDOW_DURATION - current_time
            )
            logging.warning(
                f"Throttling activated: sleeping for {sleep_time} seconds..."
            )
            time.sleep(sleep_time)

    @retry
    def get_report_page(self, rep_desc, page_nb=0):
        """
        Getting a single report page, and returning it into a raw JSON format.
        """

        self.throttle()
        rep_desc["settings"]["page"] = page_nb

        response = requests.post(
            f"https://analytics.adobe.io/api/{self.global_company_id}/reports",
            headers=self.adobe_client.build_request_headers(self.global_company_id),
            data=json.dumps(rep_desc),
        ).json()

        if response.get("message") == "Too many requests":
            raise APIRateLimitError("API rate limit was exceeded.")

        return response

    def get_parsed_report(self, rep_desc, metrics, parent_dim_parsed={}):
        """
        Iterating over report pages, parsing them, and returning a list of iterators,
        containing dictonnary-formatted records: {dimension: value, metric: value}

        The parent_dim_parsed argument (a dictionnary: {dimension: value})
        should be passed if the request includes multiple dimension breakdowns,
        so that we can add their values to output records.
        """

        report_info = {
            "parent_dim": parent_dim_parsed,
            "dim": rep_desc["dimension"].split("variables/")[1],
            "metrics": metrics,
        }
        logging.info(f"Getting report: {report_info}")

        first_response = self.get_report_page(rep_desc)
        all_responses = [parse_response(first_response, metrics, parent_dim_parsed)]

        if first_response["totalPages"] > 1:
            for page_nb in range(1, first_response["totalPages"]):
                next_response = self.get_report_page(rep_desc, page_nb)
                all_responses += [
                    parse_response(next_response, metrics, parent_dim_parsed)
                ]

        return chain(*all_responses)

    def get_node_values(self, breakdown_item_ids):
        """
        Extracting dimension values from a full report response (all pages),
        and returning them into a dictionnary of nodes: {name_itemId: value}
        For instance: {'daterangeday_1200001': 'Jan 1, 2020'}
        """

        rep_desc = self.build_report_description(
            metrics=["visits"], breakdown_item_ids=breakdown_item_ids
        )
        first_response = self.get_report_page(rep_desc)
        node_values = get_node_values_from_response(first_response)

        if first_response["totalPages"] > 1:
            for page_nb in range(1, first_response["totalPages"]):
                next_node_values = get_node_values_from_response(
                    self.get_report_page(rep_desc, page_nb)
                )
                node_values.update(next_node_values)

        return node_values

    def add_child_nodes_to_graph(self, graph, node, path_to_node):
        """
        Adding child nodes to Adobe graph, at two levels:
            parent_node: [child_node_0, child_node_1, child_node_2]
            child_node_0: []
            child_node_1: []
            child_node_2: []
        """

        logging.info(f"Adding child nodes of '{node}' to graph.")

        breakdown_item_ids = get_item_ids_from_nodes(path_to_node)
        child_node_values = self.get_node_values(breakdown_item_ids)
        self.node_values.update(child_node_values)

        graph[node] = [n for n in child_node_values]
        for n in child_node_values:
            graph[n] = []

        return graph

    def result_generator(self, data):
        yield from data

    def read_one_dimension(self):
        """
        If the requests includes only one dimension, it can be made straight away.
        """

        rep_desc = self.build_report_description(self.metrics)
        data = self.get_parsed_report(rep_desc, self.metrics)
        yield from self.result_generator(data)

    def read_through_graph(self, graph=None, node=None):
        """
        If the request includes more than one dimension, it can be made
        by exploring Adobe graph with a DFS (Deep-First-Search) algorithm.
        """

        global visited
        global path_to_node

        if not graph:
            # Create graph and add first level of nodes
            graph, node, path_to_node, visited = {}, "root", [], []
            graph = self.add_child_nodes_to_graph(graph, node, path_to_node)

        else:
            # If remaining node children to explore: add node children to graph
            if len(path_to_node) < len(self.dimensions) - 1:
                graph = self.add_child_nodes_to_graph(graph, node, path_to_node)

            # If no remaining node children to explore: get report
            if len(path_to_node) == len(self.dimensions) - 1:
                parent_dim_parsed = {
                    node.split("_")[0]: self.node_values[node] for node in path_to_node
                }
                breakdown_item_ids = get_item_ids_from_nodes(path_to_node)
                rep_desc = self.build_report_description(
                    self.metrics, breakdown_item_ids
                )
                data = self.get_parsed_report(rep_desc, self.metrics, parent_dim_parsed)
                yield from self.result_generator(data)

        # Add node to visited
        if node not in visited:
            visited.append(node)

        # Update unvisited_childs
        unvisited_childs = [
            child_node for child_node in graph[node] if child_node not in visited
        ]

        # Read through child node children
        for child_node in unvisited_childs:
            path_to_node.append(child_node)
            yield from self.read_through_graph(graph=graph, node=child_node)
            path_to_node.remove(child_node)

        # Remove local_root_node children from visited
        if path_to_node != []:
            local_root_node = path_to_node[-1]
            visited = [n for n in visited if n not in graph[local_root_node]]

    def read(self):

        if len(self.dimensions) == 1:
            yield JSONStream(
                "results_" + self.report_suite_id, self.read_one_dimension()
            )
        elif len(self.dimensions) > 1:
            yield JSONStream(
                "results_" + self.report_suite_id, self.read_through_graph()
            )
