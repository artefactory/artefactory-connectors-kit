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
from typing import Dict
from nck.config import logger

POSSIBLE_STRING_FORMATS = ["PascalCase"]


def get_dict_with_keys_converted_to_new_string_format(str_format: str = "PascalCase", **kwargs) -> Dict:
    if str_format in POSSIBLE_STRING_FORMATS and str_format == "PascalCase":
        return {to_pascal_key(key): value for key, value in kwargs.items()}
    else:
        logger.error(f"Unable to convert to new string format. Format not in {POSSIBLE_STRING_FORMATS}")
    return None


def to_pascal_key(key: str):
    return "".join(word.capitalize() for word in key.split("_"))
