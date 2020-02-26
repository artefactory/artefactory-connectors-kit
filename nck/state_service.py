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
import redis
import logging
import pickle

_state_service = None


def state():
    global _state_service
    if not _state_service:
        raise Exception("State Service has not been configured")

    return _state_service


def configure(name, host, port):
    global _state_service
    if _state_service:
        raise Exception("State Service already configured")

    _state_service = StateService(name, host, port)


class StateService(object):
    def __init__(self, name, host, port=6379):

        if host:
            logging.info("Using checkpointing service: %s:%d (%s)", host, port, name)

            self._enabled = True
            self._name = name
            self._host = host
            self._port = port
            self._client = redis.Redis(host=host, port=port)
        else:
            self._enabled = False
            logging.info("No checkpointing")

    def get(self, key, default=None):
        if not self.enabled:
            return default

        if not self._client.hexists(self._name, key):
            return default

        return pickle.loads(self._client.hget(self._name, key))

    def set(self, key, value):
        if not self.enabled:
            return

        self._client.hset(self._name, key, pickle.dumps(value))

    @property
    def enabled(self):
        return self._enabled
