import tempfile

from lib.streams.file_stream import FileStream


class TemporaryFileStream(FileStream):

    def as_file(self):
        temp = tempfile.NamedTemporaryFile()
        for line in self.readline():
            temp.write(line)
        temp.seek(0)
        return temp
