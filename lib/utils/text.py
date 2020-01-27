import logging
from typing import Dict, Generator, Union
import re


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
    line_iterator: Generator[Union[bytes, str], None, None]
) -> Generator[Dict[str, str], None, None]:
    first_line = next(line_iterator)
    headers = (
        first_line.decode("utf-8").split(",")
        if isinstance(first_line, bytes)
        else first_line.split(",")
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
        if line == "":
            break
        else:
            yield dict(zip(headers, line.split(",")))


def reformat_naming_for_bq(text, char="_"):
    text = re.sub(r"\([^()]*\)", "", text).strip()
    text = re.sub(r"[\s\W]+", char, text)
    text = re.sub(r"[" + char + "]+", char, text.strip())
    return text.lower()
