from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from bs4.element import Tag
from unidecode import unidecode
import re


def parse_response(raw_response, fields):
    for content_dct in raw_response["results"]:
        content_record = {}
        for field in fields:
            field_path = _get_field_path(field)
            field_value = _get_field_value(content_dct, field_path)
            field_as_dct = _format_field_as_dct(field, field_value)
            content_record.update(field_as_dct)
        yield content_record


# PARSE RESPONSE: Helpers


def _get_field_path(field):
    if field in CUSTOM_FIELDS:
        return CUSTOM_FIELDS[field]["source_field"].split(".")
    else:
        return field.split(".")


def _get_field_value(content_dct, field_path, visited=[]):
    path_item = field_path[0]
    remaining_path_items = len(field_path) - 1
    visited.append(path_item)
    if path_item in content_dct:
        if remaining_path_items == 0:
            return content_dct[path_item]
        else:
            return _get_field_value(content_dct[path_item], field_path[1:], visited)


def _format_field_as_dct(field, field_value):
    if field not in CUSTOM_FIELDS:
        field_as_dct = {field: field_value}
    else:
        format_function = CUSTOM_FIELDS[field]["format_function"]
        kwargs = CUSTOM_FIELDS[field]["format_function_kwargs"]
        formatted_object = format_function(field_value, **kwargs)
        if CUSTOM_FIELDS[field]["formatted_object_type"] == dict:
            field_as_dct = formatted_object
        else:
            field_as_dct = {field: formatted_object}
    return {_decode(key): _decode(value) for key, value in field_as_dct.items()}


def _decode(raw_value):
    if isinstance(raw_value, str):
        decoded_emoji = raw_value.encode("utf-16", "surrogatepass").decode("utf-16")
        return unidecode(decoded_emoji).replace("  ", " ").strip()
    else:
        return raw_value


# CUSTOM FIELDS: format functions


def _get_tiny_link(field_value: str) -> str:
    atlassian_domain = field_value["self"].split("/wiki")[0]
    shortened_path = field_value["tinyui"]
    return f"{atlassian_domain}/wiki{shortened_path}"


def _get_key_values_from_list_of_dct(field_value: List[dict], key: str) -> str:
    key_values = [dct.get(key, "") for dct in field_value]
    return "|".join(key_values)


def _get_client_properties(field_value: str) -> Optional[Dict[str, str]]:
    client_properties_dct = {}
    html_soup = BeautifulSoup(field_value, "lxml")
    DEFAULT_PROPERTIES = [
        "CONFIDENTIALITY",
        "ARTICLE STATUS",
        "INDUSTRY",
        "CLIENT COMPANY",
        "SCOPE",
        "MISSION START DATE",
        "MISSION END DATE",
        "AMOUNT SOLD",
        "MISSION TOPIC",
        "COMMERCIAL PROPOSAL",
        "ONE PAGER",
        "ARCHITECTURE",
    ]

    properties_section = _get_section_by_title(html_soup, "CASE ID CARD")
    if properties_section is not None:

        table = properties_section.table
        rows = table.find_all("tr")

        first_row_headers = rows[0].find_all("th")
        first_row_datas = rows[0].find_all("td")
        if len(first_row_headers) == 1 and len(first_row_datas) == 1:

            for row in rows:

                key = _decode(row.th.text).upper()
                text = _decode(row.td.text)
                links = [elt["href"] for elt in row.find_all("a")]

                if key in ["COMMERCIAL PROPOSAL", "ONE PAGER", "ARCHITECTURE"]:
                    client_properties_dct[key] = "|".join(links)
                elif key in ["CONFIDENTIALITY", "ARTICLE STATUS"]:
                    client_properties_dct[key] = re.sub(r"Green|Yellow|Red", "", text).upper()
                else:
                    client_properties_dct[key] = text

    return DictToClean(client_properties_dct, DEFAULT_PROPERTIES, "", "client_property_").clean()


def _get_client_completion(field_value: str) -> Optional[Dict[str, int]]:
    client_completion_dct = {}
    html_soup = BeautifulSoup(field_value, "lxml")
    DEFAULT_SECTIONS_LENGTH = {"KEY LEARNINGS": 195, "CONTEXT": 117, "APPROACH": 232, "CONCLUSION": 83}

    for required_title in DEFAULT_SECTIONS_LENGTH:
        section = _get_section_by_title(html_soup, required_title)
        if section is not None:
            text = _decode(section.text)
            section_is_completed = len(text) > DEFAULT_SECTIONS_LENGTH[required_title]
            client_completion_dct[required_title] = int(section_is_completed)

    return DictToClean(client_completion_dct, DEFAULT_SECTIONS_LENGTH.keys(), 0, "client_completion_").clean()


CUSTOM_FIELDS = {
    "tiny_link": {
        "source_field": "_links",
        "format_function": _get_tiny_link,
        "format_function_kwargs": {},
        "formatted_object_type": str,
    },
    "label_names": {
        "source_field": "metadata.labels.results",
        "format_function": _get_key_values_from_list_of_dct,
        "format_function_kwargs": {"key": "name"},
        "formatted_object_type": str,
    },
    "children_page_id": {
        "source_field": "children.page.results",
        "format_function": _get_key_values_from_list_of_dct,
        "format_function_kwargs": {"key": "id"},
        "formatted_object_type": str,
    },
    "client_properties": {
        "source_field": "body.storage.value",
        "format_function": _get_client_properties,
        "format_function_kwargs": {},
        "formatted_object_type": dict,
        "specific_to_spacekeys": ["KA"],
    },
    "client_completion": {
        "source_field": "body.storage.value",
        "format_function": _get_client_completion,
        "format_function_kwargs": {},
        "formatted_object_type": dict,
        "specific_to_spacekeys": ["KA"],
    },
}


# CUSTOM FIELDS: helpers


def _get_section_by_title(html_soup: BeautifulSoup, searched_title: str) -> Tag:
    for section in html_soup.find_all("ac:layout-section"):

        h1_elements = [_decode(h1.text).upper() for h1 in section.find_all("h1")]
        strong_elements = [_decode(strong.text).upper() for strong in section.find_all("strong")]
        section_titles = list(set(h1_elements + strong_elements))

        for title in section_titles:
            if searched_title in title:
                return section


class DictToClean:
    def __init__(self, dct, expected_keys, default_value, prefix):
        self.dct = dct
        self.expected_keys = expected_keys
        self.default_value = default_value
        self.prefix = prefix

    def clean(self):
        self._keep_expected_keys_only()
        self._add_prefix()
        return self.dct

    def _keep_expected_keys_only(self):
        self.dct = {key: self.dct[key] if key in self.dct else self.default_value for key in self.expected_keys}

    def _add_prefix(self):
        self.dct = {f"{self.prefix}{key}": value for key, value in self.dct.items()}
