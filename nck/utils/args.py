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


def deprefix(prefix, d):
    return {k.replace(prefix, "", 1): v for k, v in d.items()}


def extract_args(prefix, d, remove_prefix=True):
    args = {k: v for k, v in d.items() if k.startswith(prefix)}

    if remove_prefix:
        args = deprefix(prefix, args)

    return args


def has_arg(arg, kwargs):
    return arg in kwargs and kwargs[arg] is not None


def hasnt_arg(arg, kwargs):
    return not has_arg(arg, kwargs)
