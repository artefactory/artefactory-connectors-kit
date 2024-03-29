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

import json
import time
from datetime import timedelta
from itertools import chain

import requests
from ack.clients.adobe_analytics.client import AdobeAnalyticsClient
from ack.config import logger
from ack.readers.adobe_analytics_2_0.config import API_REQUESTS_OVER_WINDOW_LIMIT, API_WINDOW_DURATION, DATEFORMAT
from ack.readers.adobe_analytics_2_0.helper import (
    add_metric_container_to_report_description,
    get_item_ids_from_nodes,
    get_node_values_from_response,
    parse_response,
)
from ack.readers.reader import Reader
from ack.streams.json_stream import JSONStream
from ack.utils.date_handler import build_date_range
from ack.utils.exceptions import APIRateLimitError
from ack.utils.retry import retry


class AdobeAnalytics20Reader(Reader):
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
        date_range,
    ):
        self.adobe_client = AdobeAnalyticsClient(client_id, client_secret, tech_account_id, org_id, private_key)
        self.global_company_id = global_company_id
        self.report_suite_id = report_suite_id
        self.dimensions = list(dimension)
        self.metrics = list(metric)
        self.start_date, self.end_date = build_date_range(start_date, end_date, date_range)
        self.end_date = self.end_date + timedelta(days=1)
        self.ingestion_tracker = []
        self.node_values = {}

    def format_date_range(self):
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
            "globalFilters": [{"type": "dateRange", "dateRange": self.format_date_range()}],
            "metricContainer": {},
            "dimension": f"variables/{self.dimensions[len(breakdown_item_ids)]}",
            "settings": {"countRepeatInstances": "true", "limit": "5000"},
        }

        rep_desc = add_metric_container_to_report_description(
            rep_desc=rep_desc, dimensions=self.dimensions, metrics=metrics, breakdown_item_ids=breakdown_item_ids,
        )

        return rep_desc

    def throttle(self):
        """
        Monitoring API rate limit (12 requests every 6 seconds).
        """

        current_time = time.time()
        self.ingestion_tracker.append(current_time)
        window_ingestion_tracker = [t for t in self.ingestion_tracker if t >= (current_time - API_WINDOW_DURATION)]

        if len(window_ingestion_tracker) >= API_REQUESTS_OVER_WINDOW_LIMIT:
            sleep_time = window_ingestion_tracker[0] + API_WINDOW_DURATION - current_time
            logger.warning(f"Throttling activated: sleeping for {sleep_time} seconds...")
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
        logger.info(f"Getting report: {report_info}")

        first_response = self.get_report_page(rep_desc)
        all_responses = [parse_response(first_response, metrics, parent_dim_parsed)]

        if first_response["totalPages"] > 1:
            for page_nb in range(1, first_response["totalPages"]):
                next_response = self.get_report_page(rep_desc, page_nb)
                all_responses += [parse_response(next_response, metrics, parent_dim_parsed)]

        return chain(*all_responses)

    def get_node_values(self, breakdown_item_ids):
        """
        Extracting dimension values from a full report response (all pages),
        and returning them into a dictionnary of nodes: {name_itemId: value}
        For instance: {'daterangeday_1200001': 'Jan 1, 2020'}
        """

        rep_desc = self.build_report_description(metrics=["visits"], breakdown_item_ids=breakdown_item_ids)
        first_response = self.get_report_page(rep_desc)
        node_values = get_node_values_from_response(first_response)

        if first_response["totalPages"] > 1:
            for page_nb in range(1, first_response["totalPages"]):
                next_node_values = get_node_values_from_response(self.get_report_page(rep_desc, page_nb))
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

        logger.info(f"Adding child nodes of '{node}' to graph.")

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
                parent_dim_parsed = {node.split("_")[0]: self.node_values[node] for node in path_to_node}
                breakdown_item_ids = get_item_ids_from_nodes(path_to_node)
                rep_desc = self.build_report_description(self.metrics, breakdown_item_ids)
                data = self.get_parsed_report(rep_desc, self.metrics, parent_dim_parsed)
                yield from self.result_generator(data)

        # Add node to visited
        if node not in visited:
            visited.append(node)

        # Update unvisited_childs
        unvisited_childs = [child_node for child_node in graph[node] if child_node not in visited]

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
            yield JSONStream("results_" + self.report_suite_id, self.read_one_dimension())
        elif len(self.dimensions) > 1:
            yield JSONStream("results_" + self.report_suite_id, self.read_through_graph())
