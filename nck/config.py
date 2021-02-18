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
import sys
import os

LEVEL = logging.INFO
if "LOGGING_LEVEL" in os.environ:
    LEVEL = os.environ["LOGGING_LEVEL"]
FORMAT = "%(asctime)s - (%(name)s) - %(levelname)s - %(message)s"
HANDLERS = [logging.StreamHandler(sys.stdout)]

logging.basicConfig(level=LEVEL, format=FORMAT, handlers=HANDLERS)
logger = logging.getLogger()

# The below snippet is used in the following modules:
# - nck/readers/objectstorage_reader.py
# - nck/writers/gcs_writer.py
# - nck/writers/bigquery_writer.py
for key, var in os.environ.items():
    locals()[key] = var
