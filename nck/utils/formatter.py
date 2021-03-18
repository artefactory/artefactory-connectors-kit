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
import os
from datetime import datetime

from nck.utils.file_reader import read_json
from nck.readers import reader_classes
from nck.writers import writer_classes

DATEFORMAT = "%Y-%m-%d"


def format_writers(writers):
    writers_list = []
    for writer in writers:
        writer_name = writer.pop("name")
        config_file_path = f"{os.getcwd()}/nck/writers/{writer_name}/config.json"
        args = _format_args(config_file_path, writer)
        writers_list.append(writer_classes[writer_name](**args))

    return writers_list


def format_reader(reader):
    reader_name = reader.pop("name")
    config_file_path = f"{os.getcwd()}/nck/readers/{reader_name}/config.json"
    args = _format_args(config_file_path, reader)
    return reader_classes[reader_name](**args)


def _format_args(config_file_path: str, args: dict) -> dict:
    config = read_json(config_file_path)
    config_properties = config["properties"]

    if args:
        # if args isn't empty
        for key, value in config_properties.items():
            if value["type"] == "array":
                if key in args.keys():
                    if isinstance(args[key], list):
                        res = []
                        for arg_value in args[key]:
                            res.append(_format_arg(arg_value, value["items"]["type"]))
                        args[key] = res
                    else:
                        args[key] = (_format_arg(args[key], value["items"]["type"]),)
                elif "default" in value["items"].keys():
                    args[key] = (_format_arg(value["items"]["default"], value["items"]["type"]),)
                else:
                    args[key] = ()
            else:
                if key in args.keys():
                    args[key] = _format_arg(args[key], value["type"])
                elif "default" in value.keys():
                    args[key] = _format_arg(value["default"], value["type"])
                else:
                    args[key] = None

    return args


def _format_arg(arg_value, arg_type: str):
    if arg_type == "string" or arg_type == "boolean":
        value = arg_value
    elif arg_type == "float":
        value = float(arg_value)
    elif arg_type == "integer":
        value = int(arg_value)
    elif arg_type == "datetime":
        value = datetime.strptime(arg_value, DATEFORMAT)
    else:
        raise ValueError(f"In the config file, the given argument's type ({arg_type}) is unknown or not supported.")

    return value
