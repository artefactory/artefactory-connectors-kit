import datetime
import binascii
import uuid
import hashlib
import more_itertools
import logging
import json

## Credit goes to Mr Martin Winkel for the base code provided : 
## github : https://github.com/SaturnFromTitan/adobe_analytics

def _serialize_header(properties):
    header = ['{key}="{value}"'.format(key=k, value=v) for k, v in properties.items()]
    return ', '.join(header)


def build_headers(password, username):
        nonce = str(uuid.uuid4())
        base64nonce = binascii.b2a_base64(binascii.a2b_qp(nonce))
        created_date = datetime.datetime.utcnow().isoformat() + 'Z'
        sha = nonce + created_date + password
        sha_object = hashlib.sha1(sha.encode())
        password_64 = binascii.b2a_base64(sha_object.digest())
        
        properties = {
            "Username": username,
            "PasswordDigest": password_64.decode().strip(),
            "Nonce": base64nonce.decode().strip(),
            "Created": created_date
        }
        header = 'UsernameToken ' + _serialize_header(properties)
        return {'X-WSSE': header}





def _parse_header(report):
    dimensions = [_classification_or_name(dimension) for dimension in report["elements"]]
    metrics = [metric["name"] for metric in report["metrics"]]
    return dimensions, metrics


def _classification_or_name(element):
    if "classification" in element:
        return element["classification"]
    return element["name"]

def _fix_header(dimensions, metrics, data):
    header = dimensions + metrics
    if len(header) != len(data[0]):  # can only be when granularity breakdown is used
        return ["Datetime"] + header
    return header

import datetime
import numpy as np
import pandas as pd


def _parse_data(data, metric_count):
    """
    Recursive parsing of the "data" part of the Adobe response.
    :param data: list of dicts and lists. quite a complicated structure
    :param metric_count: int, number of metrics in report
    :return: list of lists
    """
    #logger.debug("Parsing report data (recursively).")
    if len(data) > 0 and "breakdown" in data[0]:
        rows = list()
        for  chunk in data:
            dim_value = _dimension_value(chunk)
            #import ipdb; ipdb.set_trace()
            if "breakdown" in chunk:
                for row in _parse_data(chunk["breakdown"], metric_count):
                    rows.append([dim_value] + row)
            else:
                rows.append(_parse_most_granular([chunk], metric_count))
            #rows += [[dim_value] + row
             #        for row in _parse_data(chunk["breakdown"], metric_count)]
        return rows
    else:
        return _parse_most_granular(data, metric_count)


def _parse_most_granular(data, metric_count):
    """
    Parsing of the most granular part of the response.
    It is different depending on if there's a granularity breakdown or not
    :param data: dict
    :param metric_count: int, number of metrics in report
    :return: list of lists
    """
    # logger.debug("Parsing most granular level of data.")
    rows = list()
    for chunk in data:
        part_rows = [(val if val != "" else np.nan) for val in chunk["counts"]]
        # data alignment is a bit different if adding granularity breakdowns
        if len(chunk["counts"]) > metric_count:
            part_rows = more_itertools.chunked(iterable=part_rows, n=metric_count + 1)
        else:
            part_rows = [part_rows]

        dim_value = _dimension_value(chunk)
        rows += [[dim_value] + part_row for part_row in part_rows]
    return rows


def _dimension_value(chunk):
    if _dimension_value_is_nan(chunk):
        return np.nan
    elif "year" in chunk:
        return _to_datetime(chunk)
    else:
        return chunk["name"]


def _dimension_value_is_nan(chunk):
    return ("name" not in chunk) or (chunk["name"] == "") or (chunk["name"] == "::unspecified::")

def _to_datetime(chunk):
    time_stamp = datetime.datetime(
        year=chunk["year"],
        month=chunk["month"],
        day=chunk["day"],
        hour=chunk.get("hour", 0)
    )
    return time_stamp.strftime("%Y-%m-%d %H:00:00")

def parse(raw_response):
        report = raw_response["report"]
        raw_data = report["data"]
        dimensions, metrics = _parse_header(report)
        data = _parse_data(raw_data, metric_count=len(metrics))
        headers = _fix_header(dimensions, metrics, data)
        for row in data:    
            yield {headers[i]:row[i] for i in range(len(headers))} 
        #return ({el:hd for hd in headers} for el in data)

class ReportNotReadyError(Exception):
    def __init__(self, message):
        super().__init__(message)
        logging.error(message)
        