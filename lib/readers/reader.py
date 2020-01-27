import lib.state_service as state


class Reader(object):
    @property
    def state(self):
        return state.state()

    def read(self):
        """
        The read method takes no arguments, and should return a generator of stream objects.
        Each stream instance yielded should represent a file to write and have it's own name.
        """
        raise NotImplementedError
