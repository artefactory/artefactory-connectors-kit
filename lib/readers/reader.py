import datetime
import time

from lib.streams.stream import StreamCollection


class BaseReader():

    _stream_collection = StreamCollection()
    _stream = None

    def collection(self):
        self.populate()
        return self._stream_collection.list()

    def populate(self):
        self.connect()
        for element in self.list():
            name, content = self.read(element)
            stream = self._stream(name, content)
            self._stream_collection.add(stream)
        self.close()

    def list(self):
        """
            List all elements to be read by current NCK execution
            return:
                List of files, queries to be read
        """
        pass

    def connect(self):
        """
            Instance connection with distant source
        """
        pass

    def read(self, element):
        """
            Read `element` and return element name and element content
            attr:
                element (str): Element name, could be filename, query, etc.

            return:
                Tuple (name (str), element (IO, Array, etc.)): Name of the element and its content
        """
        pass

    def close(self):
        """
            Close connection with distant source
        """
        pass
