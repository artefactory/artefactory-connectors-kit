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
