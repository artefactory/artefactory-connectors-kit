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
from nck.config import logger
import re
import csv
from io import StringIO
from collections import deque
from itertools import islice


def get_report_generator_from_flat_file(
    line_iterator,
    delimiter=",",
    skip_n_first=0,
    skip_n_last=0,
    add_column=False,
    column_dict={},
):
    """
    From the line iterator of a flat file:
        [
            "Date,AdvertiserId,Impressions",
            "2020-01-01,1234,10",
            "2020-01-01,5678,20"
        ]
    Return a generator of {column: value} dictionnaries:
        [
            {"Date": "2020-01-01", "AdvertiserId": "1234", "Impressions": "10"},
            {"Date": "2020-01-01", "AdvertiserId": "5678", "Impressions": "20"}
        ]
    Params
        :line_iterator (iter): line iterator of the file to process
        :delimiter (str): delimiter to parse file lines
        :skip_n_first (int): nb of lines to skip at begining of file (excl. blank lines)
        :skip_n_last (int): nb of lines to skip at end of file (excl. blank lines)
        :add_column (bool): wether to add a fixed {column: value} at the end of each record
        :column_dict (dict): if add_column is True, {column: value} dictionnary
        to add at the end of each record (can include multiple column_names)
    """

    first_line = True
    for line in skip(line_iterator, skip_n_first, skip_n_last):
        line = decode_if_needed(line)
        if first_line:
            first_line = False
            headers = parse_decoded_line(line, delimiter)
        else:
            parsed_line = parse_decoded_line(line, delimiter)
            if len(parsed_line) != len(headers):
                logger.warning(f"Skipping line '{line}': length of parsed line doesn't match length of headers.")
            else:
                record = dict(zip(headers, parsed_line))
                if add_column:
                    yield {**record, **column_dict}
                else:
                    yield record


def decode_if_needed(line):
    if isinstance(line, bytes):
        try:
            line = line.decode("utf-8")
        except UnicodeDecodeError as e:
            logger.warning(
                "An error has occurred while parsing the file."
                f"The line could not be decoded in {e.encoding}."
                f"Invalid input that the codec failed on: {e.object[e.start : e.end]}"
            )
            line = line.decode("utf-8", errors="ignore")
    return line


def parse_decoded_line(line, delimiter=",", quotechar='"'):
    line_as_file = StringIO(line)
    reader = csv.reader(
        line_as_file,
        delimiter=delimiter,
        quotechar=quotechar,
        quoting=csv.QUOTE_ALL,
        skipinitialspace=True,
    )
    return next(reader)


def skip(iterator, n_first, n_last):
    """
    Skips the n first and/or n last lines of a line iterator,
    from which blank lines have been removed
    """
    iterator = skip_blank(iterator)
    if n_first > 0:
        iterator = skip_first(iterator, n_first)
    if n_last > 0:
        iterator = skip_last(iterator, n_last)
    yield from iterator


def skip_blank(iterator):
    for item in iterator:
        if item:
            yield item


def skip_first(iterator, n):
    yield from islice(iterator, n, None)


def skip_last(iterator, n):
    previous_items = deque(islice(iterator, n), n)
    for item in iterator:
        yield previous_items.popleft()
        previous_items.append(item)


def reformat_naming_for_bq(text, char="_"):
    text = re.sub(r"\([^()]*\)", "", text).strip()
    text = re.sub(r"[\s\W]+", char, text)
    text = re.sub(r"[" + char + "]+", char, text.strip())
    return text.lower()


def strip_prefix(text, prefix):
    return re.split(prefix, text)[-1]
