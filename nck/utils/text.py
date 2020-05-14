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
from typing import Dict, Generator, List, Union
import re
import csv
from io import StringIO

from nck.utils.date_handler import get_date_start_and_date_stop_from_range


def add_column_value_to_csv_line_iterator(line_iterator, columname, value):
    first_line = True
    for line in line_iterator:
        if line == "":
            break
        if first_line:
            first_line = False
            if columname in line.split(","):
                raise Exception("Column {} already present".format(columname))
            yield line + "," + columname
        else:
            yield line + "," + value


def get_generator_dict_from_str_csv(
    line_iterator: Generator[Union[bytes, str], None, None], add_date=False, day_range=None, date_format="%Y-%m-%d"
) -> Generator[Dict[str, str], None, None]:
    first_line = next(line_iterator)
    headers = (
        parse_decoded_line(first_line.decode("utf-8"))
        if isinstance(first_line, bytes)
        else parse_decoded_line(first_line)
    )
    if add_date:
        headers.extend(["date_start", "date_stop"])

    next_line = next(line_iterator, None)
    while next_line is not None:
        current_line = next_line
        if isinstance(current_line, bytes):
            try:
                current_line = current_line.decode("utf-8")
            except UnicodeDecodeError as err:
                logging.warning(
                    "An error has occurred while parsing the file. "
                    "The line could not be decoded in %s."
                    "Invalid input that the codec failed on: %s",
                    err.encoding,
                    err.object[err.start : err.end],
                )
                current_line = current_line.decode("utf-8", errors="ignore")

        next_line = next(line_iterator, "")
        if len(next_line) == 0:
            break

        if add_date:
            start, end = get_date_start_and_date_stop_from_range(day_range)
            current_line += f",{start.strftime(date_format)},{end.strftime(date_format)}"

        yield dict(zip(headers, parse_decoded_line(current_line)))


def get_generator_dict_from_str_tsv(
    line_iterator: Generator[Union[bytes, str], None, None], skip_first_row=False
) -> Generator[Dict[str, str], None, None]:
    if skip_first_row:
        next(line_iterator)
    headers_line = next(line_iterator)
    headers = (
        parse_decoded_line(headers_line.decode("utf-8"), delimiter="\t")
        if isinstance(headers_line, bytes)
        else parse_decoded_line(headers_line, delimiter="\t")
    )
    for line in line_iterator:
        if isinstance(line, bytes):
            try:
                line = line.decode("utf-8")
            except UnicodeDecodeError as err:
                logging.warning(
                    "An error has occured while parsing the file. "
                    "The line could not be decoded in %s."
                    "Invalid input that the codec failed on: %s",
                    err.encoding,
                    err.object[err.start : err.end],
                )
                line = line.decode("utf-8", errors="ignore")

        yield dict(zip(headers, parse_decoded_line(line, delimiter="\t")))


def parse_decoded_line(line: str, delimiter=",", quotechar='"') -> List[str]:
    line_as_file = StringIO(line)
    reader = csv.reader(
        line_as_file, delimiter=delimiter, quotechar=quotechar, quoting=csv.QUOTE_ALL, skipinitialspace=True
    )
    return next(reader)


def reformat_naming_for_bq(text, char="_"):
    text = re.sub(r"\([^()]*\)", "", text).strip()
    text = re.sub(r"[\s\W]+", char, text)
    text = re.sub(r"[" + char + "]+", char, text.strip())
    return text.lower()
