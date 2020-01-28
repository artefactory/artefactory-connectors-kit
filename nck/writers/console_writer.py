import click
import sys

from nck.writers.writer import Writer
from nck.commands.command import processor
from nck.utils.args import extract_args


@click.command(name="write_console")
@processor()
def console(**kwargs):
    return ConsoleWriter(**extract_args("console_", kwargs))


class ConsoleWriter(Writer):
    def __init__(self):
        pass

    def write(self, stream):
        """
            Write file to console, mainly used for debugging
        """
        # this is how to read from a file as stream
        file = stream.as_file()
        buffer = "buf"
        while len(buffer) > 0:
            buffer = file.read(1024)
            sys.stdout.buffer.write(buffer)
