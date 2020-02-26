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
from nck.readers.radarly_reader import RadarlyReader
from unittest import TestCase, mock
from unittest.mock import MagicMock

import logging
from datetime import datetime, timedelta
from typing import Tuple
import numpy as np
import json


def create_mock_payload(
    start_date: datetime, end_date: datetime
) -> Tuple[datetime, datetime, int]:
    return (start_date, end_date, int((end_date - start_date).total_seconds() * 2))


def create_mock_publications_iterator(
    param: Tuple[datetime, datetime, int]
) -> MagicMock:
    start_date, end_date, total = param
    delta = (end_date - start_date).total_seconds()
    mock_publications_iterator = MagicMock()
    mocked_publications = iter(
        [
            {"date": start_date + timedelta(x), "text": "random text"}
            for x in np.linspace(start=0, stop=delta, num=total)
        ]
    )
    mock_publications_iterator.__iter__.return_value = mocked_publications
    mock_publications_iterator.__next__ = lambda x: next(mocked_publications)
    mock_publications_iterator.total = total

    return mock_publications_iterator


class RadarlyReaderTest(TestCase):
    @mock.patch("nck.readers.radarly_reader.RadarlyApi")
    @mock.patch("nck.readers.radarly_reader.Project")
    @mock.patch("nck.readers.radarly_reader.RadarlyReader.get_payload")
    def test_read(self, mock_get_payload, mock_Project, mock_RadarlyApi):
        mock_RadarlyApi.init.side_effect = lambda client_id, client_secret: logging.info(
            "Mock RadarlyApi successfully initiated"
        )
        mock_get_payload.side_effect = create_mock_payload
        mock_project_object = MagicMock()
        mock_project_object.get_all_publications = create_mock_publications_iterator
        mock_Project.find.return_value = mock_project_object

        reader = RadarlyReader(
            pid=1,
            client_id="xxx",
            client_secret="xxx",
            focus_id=(1, 2, 3),
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2020, 1, 1, 3),
            api_request_limit=250,
            api_date_period_limit=10000,
            api_quarterly_posts_limit=45000,
            api_window=300,
            throttle=True,
            throttling_threshold_coefficient=0.95,
        )

        for stream in reader.read():
            line = stream.as_file().readline()
            line = json.loads(line)
            assert "date" in line.keys()
            assert "text" in line.keys()
