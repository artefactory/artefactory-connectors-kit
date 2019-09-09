import click
import sys

from lib.writers.writer import Writer
from lib.commands.command import processor
from lib.utils.args import extract_args


@click.command(name="write_console")
@processor()
def console(**kwargs):
    return ConsoleWriter(**extract_args('console_', kwargs))


class ConsoleWriter(Writer):

    def __init__(self):
        pass

    def write(self, stream):
        """
            Write file to console, mainly used for debugging
        """

        for line in stream.as_file():
            sys.stdout.write(line.decode(sys.stdout.encoding))
