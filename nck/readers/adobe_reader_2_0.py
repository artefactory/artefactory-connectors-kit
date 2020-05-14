import click
import json
import logging
import datetime
import requests
import time
from itertools import chain

from nck.utils.args import extract_args
from nck.commands.command import processor
from nck.readers.reader import Reader
from nck.clients.adobe_client import JWTClient
from nck.streams.json_stream import JSONStream
from nck.helpers.adobe_helper_2_0 import (
    build_request_headers,
    add_metric_container_to_report_description,
    get_node_values_from_response,
    get_item_ids_from_nodes,
    parse_response,
)

DATEFORMAT = "%Y-%m-%dT%H:%M:%S"
API_WINDOW_DURATION = 6
API_REQUESTS_OVER_WINDOW_LIMIT = 12

logging.basicConfig(level="INFO")
logger = logging.getLogger()


@click.command(name="read_adobe_2_0")
@click.option("--adobe-api-key", required=True)
@click.option("--adobe-tech-account-id", required=True)
@click.option("--adobe-org-id", required=True)
@click.option("--adobe-client-secret", required=True)
@click.option("--adobe-metascopes", required=True)
@click.option("--adobe-private-key-path", required=True)
@click.option("--adobe-date-start", required=True, type=click.DateTime())
@click.option("--adobe-date-stop", required=True, type=click.DateTime())
@click.option("--adobe-report-suite-id", required=True)
@click.option("--adobe-dimensions", required=True, multiple=True)
@click.option("--adobe-metrics", required=True, multiple=True)
@processor(
    "adobe_api_key",
    "adobe_tech_account_id",
    "adobe_org_id",
    "adobe_client_secret",
    "adobe_metascopes",
    "adobe_private_key_path",
)
def adobe_2_0(**kwargs):
    return AdobeReader_2_0(**extract_args("adobe_", kwargs))


class AdobeReader_2_0(Reader):
    def __init__(
        self,
        api_key,
        tech_account_id,
        org_id,
        client_secret,
        metascopes,
        private_key_path,
        date_start,
        date_stop,
        report_suite_id,
        dimensions,
        metrics,
    ):
        # We should probably define a method to create the jwt_client within the NewAdobeReader
        self.jwt_client = JWTClient(
            api_key,
            tech_account_id,
            org_id,
            client_secret,
            metascopes,
            private_key_path,
        )
        self.date_start = date_start
        self.date_stop = date_stop + datetime.timedelta(days=1)
        self.report_suite_id = report_suite_id
        self.dimensions = dimensions
        self.metrics = metrics
        self.node_values = {}

    def build_date_range(self):
        return f"{self.date_start.strftime(DATEFORMAT)}/{self.date_stop.strftime(DATEFORMAT)}"

    def build_report_description(self, breakdown_item_ids, metrics):
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
            "dimension": "variables/{}".format(
                self.dimensions[len(breakdown_item_ids)]
            ),
            "settings": {"countRepeatInstances": "true", "limit": "500"},
        }

        rep_desc = add_metric_container_to_report_description(
            rep_desc=rep_desc,
            dimensions=self.dimensions,
            breakdown_item_ids=breakdown_item_ids,
            metrics=metrics,
        )

        return rep_desc

    def get_report_page(self, rep_desc, page_nb=0):
        """
        Getting a single report page, and returning it into a raw JSON format.
        """
        global tracker

        # Pause if API rate limit is enforced (12 requests every 6 seconds)

        current_time = time.time()
        tracker.append(current_time)
        tracker_over_window = [
            t for t in tracker if t >= (current_time - API_WINDOW_DURATION)
        ]

        if len(tracker_over_window) >= API_REQUESTS_OVER_WINDOW_LIMIT:
            sleep_time = tracker_over_window[0] + API_WINDOW_DURATION - current_time
            logging.warning(
                "Throttling activated: sleeping for {} seconds...".format(sleep_time)
            )
            time.sleep(sleep_time)

        # Make request

        rep_desc["settings"]["page"] = page_nb
        report_available = False

        while not report_available:

            response = requests.post(
                "https://analytics.adobe.io/api/{}/reports".format(
                    self.jwt_client.global_company_id
                ),
                headers=build_request_headers(self.jwt_client),
                data=json.dumps(rep_desc),
            ).json()

            if response.get("message") == "Too many requests":
                logging.warning(
                    "Throttling activated: sleeping for {} seconds...".format(
                        API_WINDOW_DURATION
                    )
                )
                time.sleep(API_WINDOW_DURATION)
            else:
                report_available = True

        return response

    def get_parsed_report(self, rep_desc, metrics, parent_dim_parsed):
        """
        Iterating over report pages, parsing them, and returning a list of iterators,
        containing dictonnary-formatted records: {dimension: value, metric: value}

        The parent_dim_parsed argument (a dictionnary: {dimension: value})
        should be passed if the request includes multiple dimension breakdowns,
        so that we can add their values to output records.
        """

        logging.info(f"Getting report: {rep_desc}")

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
            breakdown_item_ids=breakdown_item_ids, metrics=["visits"]
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

        breakdown_item_ids = get_item_ids_from_nodes(path_to_node)
        child_node_values = self.get_node_values(breakdown_item_ids)
        self.node_values.update(child_node_values)

        graph[node] = [n for n in child_node_values]
        for n in child_node_values:
            graph[n] = []

        return graph

    def result_generator(self, data):
        yield from data

    def read_through_graph(self, graph=None, node=None):
        """
        Exploring Adobe graph using a DFS (Deep-First-Search) algorithm.
        """

        global visited
        global path_to_node
        global tracker

        if graph:

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
                    breakdown_item_ids, self.metrics
                )
                data = self.get_parsed_report(rep_desc, self.metrics, parent_dim_parsed)

                yield from self.result_generator(data)

        else:
            # Create graph and add first level of nodes
            graph, node, path_to_node, visited, tracker = {}, "root", [], [], []
            graph = self.add_child_nodes_to_graph(graph, node, path_to_node)

        # Add node to visited
        if node not in visited:
            visited.append(node)

        # Update unvisited_childs
        unvisited_childs = [
            child_node for child_node in graph[node] if child_node not in visited
        ]

        # Read through node children
        for child_node in unvisited_childs:
            path_to_node.append(child_node)
            yield from self.read_through_graph(graph=graph, node=child_node)
            path_to_node.remove(child_node)

        # Remove local_root_node children from visited
        if path_to_node != []:
            local_root_node = path_to_node[-1]
            visited = [n for n in visited if n not in graph[local_root_node]]

    def read(self):
        yield JSONStream("adobe_results", self.read_through_graph())
