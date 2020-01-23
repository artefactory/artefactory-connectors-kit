import click
import logging
import datetime
import json
from time import sleep
from itertools import chain
from lib.commands.command import processor
from lib.readers.reader import Reader
from lib.utils.args import extract_args
from lib.utils.retry import retry
from lib.streams.json_stream import JSONStream
import requests
from lib.helpers.adobe_helper import build_headers, ReportNotReadyError, parse

# Credit goes to Mr Martin Winkel for the base code provided :
# github : https://github.com/SaturnFromTitan/adobe_analytics

DISCOVERY_URI = "https://analyticsreporting.googleapis.com/$discovery/rest"

LIMIT_NVIEWS_PER_REQ = 5

ADOBE_API_ENDPOINT = "https://api.omniture.com/admin/1.4/rest/"

MAX_WAIT_REPORT_DELAY = 4096


@click.command(name="read_adobe")
@click.option("--adobe-password", required=True)
@click.option("--adobe-username", required=True)
@click.option("--adobe-list-report-suite", type=click.BOOL, default=False)
@click.option("--adobe-report-suite-id")
@click.option("--adobe-report-element-id", multiple=True)
@click.option("--adobe-report-metric-id", multiple=True)
@click.option("--adobe-date-granularity", default=None)
@click.option(
    "--adobe-day-range",
    type=click.Choice(["PREVIOUS_DAY", "LAST_30_DAYS", "LAST_7_DAYS", "LAST_90_DAYS"]),
    default=None,
)
@click.option("--adobe-start-date", type=click.DateTime())
@click.option("--adobe-end-date", default=None, type=click.DateTime())
@processor("adobe_password", "adobe_username")
def adobe(**kwargs):
    # Should handle valid combinations dimensions/metrics in the API
    return AdobeReader(**extract_args("adobe_", kwargs))


class AdobeReader(Reader):
    def __init__(self, password, username, **kwargs):
        self.password = password
        self.username = username
        self.kwargs = kwargs

    def request(self, api, method, data=None):
        """ Compare with https://marketing.adobe.com/developer/api-explorer """
        api_method = "{0}.{1}".format(api, method)
        data = data or dict()
        logging.info("{}.{} {}".format(api, method, data))
        response = requests.post(
            ADOBE_API_ENDPOINT,
            params={"method": api_method},
            data=json.dumps(data),
            headers=build_headers(self.password, self.username),
        )
        json_response = response.json()
        logging.debug("Response: {}".format(json_response))
        return json_response

    def build_report_description(self):
        report_description = {
            "reportDescription": {
                "reportSuiteID": self.kwargs.get("report_suite_id"),
                "elements": [
                    {"id": el} for el in self.kwargs.get("report_element_id", [])
                ],
                "metrics": [
                    {"id": mt} for mt in self.kwargs.get("report_metric_id", [])
                ],
            }
        }
        self.set_date_gran_report_desc(report_description)
        self.set_date_range_report_desc(report_description)
        logging.debug(f"report_decription content {report_description}")
        return report_description

    def get_days_delta(self):
        days_range = self.kwargs.get("day_range")
        if days_range == "PREVIOUS_DAY":
            days_delta = 1
        elif days_range == "LAST_7_DAYS":
            days_delta = 7
        elif days_range == "LAST_30_DAYS":
            days_delta = 30
        elif days_range == "LAST_90_DAYS":
            days_delta = 90
        else:
            raise Exception("{} is not handled by the reader".format(days_range))
        return days_delta

    def set_date_range_report_desc(self, report_description):
        if self.kwargs.get("date_range") != ():
            start_date = self.kwargs.get("start_date")
            end_date = self.kwargs.get("end_date", datetime.datetime.now())
        else:
            end_date = datetime.datetime.now().date()
            start_date = end_date - datetime.timedelta(days=self.get_days_delta())
        report_description["reportDescription"]["dateFrom"] = start_date.strftime(
            "%Y-%m-%d"
        )
        report_description["reportDescription"]["dateTo"] = end_date.strftime(
            "%Y-%m-%d"
        )

    def set_date_gran_report_desc(self, report_description):
        if self.kwargs.get("date_granularity", None) is not None:
            report_description["reportDescription"][
                "dateGranularity"
            ] = self.kwargs.get("date_granularity")

    @retry
    def query_report(self):
        query_report = self.request(
            api="Report", method="Queue", data=self.build_report_description()
        )
        return query_report

    @retry
    def get_report(self, report_id, page_number=1):
        request_f = lambda : self.request(
            api="Report",
            method="Get",
            data={"reportID": report_id, "page": page_number},
        )
        response = request_f()
        idx = 1
        while response.get("error") == "report_not_ready":
            logging.info(f"waiting {idx} s for report to be ready")
            sleep(idx + 1)
            if idx + 1 > MAX_WAIT_REPORT_DELAY:
                raise ReportNotReadyError(f"waited too long for report to be ready")
            idx = idx * 2
            response = request_f()
        return response

    def download_report(self, rep_id):
        raw_response = self.get_report(rep_id, page_number=1)
        all_responses = [parse(raw_response)]
        if "totalPages" in raw_response["report"]:
            all_responses = all_responses + [
                parse(self.get_report(rep_id, page_number=np))
                for np in range(2, raw_response["report"]["totalPages"] + 1)
            ]
        return chain(*all_responses)

    def read(self):
        if self.kwargs.get("list_report_suite", False):
            r = self.request("Company", "GetReportSuites")
            data = r["report_suites"]
            idf = "list_rps"
        else:
            query_rep = self.query_report()
            rep_id = query_rep["reportID"]
            data = self.download_report(rep_id)
            idf = "report_" + str(rep_id)

        def result_generator():
            for record in data:
                yield record

        yield JSONStream("results_" + idf, result_generator())
