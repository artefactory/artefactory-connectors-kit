import logging
import click
import json
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
@click.option("--adobe-dimension", required=True, multiple=True)
@click.option("--adobe-metric", required=True, multiple=True)
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
        dimension,
        metric,
    ):
        # JWT authentification will be changed to OAth authentification
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
        self.dimensions = list(dimension)
        self.metrics = list(metric)
        self.ingestion_tracker = []
        self.node_values = {}

    def build_date_range(self):
        return f"{self.date_start.strftime(DATEFORMAT)}/{self.date_stop.strftime(DATEFORMAT)}"

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
            "dimension": "variables/{}".format(
                self.dimensions[len(breakdown_item_ids)]
            ),
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

    def get_report_page(self, rep_desc, page_nb=0):
        """
        Getting a single report page, and returning it into a raw JSON format.
        """

        self.throttle()
        rep_desc["settings"]["page"] = page_nb

        # As throttling failed occasionnaly, we had to include a back-up check
        report_available = False
        while not report_available:

            response = requests.post(
                f"https://analytics.adobe.io/api/{self.jwt_client.global_company_id}/reports",
                headers=build_request_headers(self.jwt_client),
                data=json.dumps(rep_desc),
            ).json()

            if response.get("message") == "Too many requests":
                logging.warning(
                    f"Throttling activated: sleeping for {API_WINDOW_DURATION} seconds..."
                )
                time.sleep(API_WINDOW_DURATION)
            else:
                report_available = True

        return response

    def get_parsed_report(self, rep_desc, metrics, parent_dim_parsed={}):
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
