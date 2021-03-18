class NewStream:
    def __init__(self, name, stream):
        self.name = name
        self.stream = stream
        self.stream.seek(0)
