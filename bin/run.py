import click

from lib.writers import writers, Writer
from lib.readers import readers, Reader


@click.group(chain=True)
def app():
    pass


@app.resultcallback()
def run(processors):
    processor_instances = [p() for p in processors]

    _readers = filter(lambda o: isinstance(o, Reader), processor_instances)
    _writers = filter(lambda o: isinstance(o, Writer), processor_instances)

    if len(_readers) < 1:
        raise click.BadParameter("You must specify a reader")

    if len(_readers) > 1:
        raise click.BadParameter("You cannot specify multiple readers")

    if len(_writers) < 1:
        raise click.BadParameter("You must specify at least one writer")

    reader = _readers[0]

    for stream in reader.read():
        for writer in _writers:
            writer.write(stream)


def build_commands():
    for writer in writers:
        app.add_command(writer)

    for reader in readers:
        app.add_command(reader)


if __name__ == '__main__':
    build_commands()
    app()
