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
import pickle

import redis


class RedisStateService:
    def __init__(self, name, host, port=6379):
        if host:
            logger.info(f"Using checkpointing service: {host}:{port} ({name})")
            self._enabled = True
            self._name = name
            self._host = host
            self._port = port
            self._client = redis.Redis(host=host, port=port)
        else:
            self._enabled = False
            logger.info("No checkpointing")

    def get(self, key):
        if self._enabled and self._client.hexists(self._name, key):
            return pickle.loads(self._client.hget(self._name, key))

    def set(self, key, value):
        if self._enabled:
            self._client.hset(self._name, key, pickle.dumps(value))
