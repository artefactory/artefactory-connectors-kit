import lib.state_service as state


class Reader(object):

    @property
    def state(self):
        return state.state()

    def read(self):
        """
        The read method takes no arguments, and returns a generator of dicts
        """
        raise NotImplementedError
