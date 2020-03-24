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
from typing import Dict, Any
import logging

logging.getLogger("ApiClient")

POSSIBLE_STRING_FORMATS = ["PascalCase"]


def get_dict_with_keys_converted_to_new_string_format(
    dictionary: Dict[str, Any], str_format: str = "PascalCase"
) -> Dict:
    if str_format in POSSIBLE_STRING_FORMATS and str_format == "PascalCase":
        new_keys = [
            "".join(word.capitalize() for word in old_key.split("_"))
            for old_key in dictionary
        ]
        old_keys = dictionary.copy().keys()
        for old_key, new_key in zip(old_keys, new_keys):
            dictionary[new_key] = dictionary.pop(old_key)
        return dictionary
    else:
        logging.error((
            "Unable to convert to new string format. "
            "Format not in %s"
        ) % POSSIBLE_STRING_FORMATS)
    return None
