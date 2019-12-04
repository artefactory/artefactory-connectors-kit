import click

from lib.writers import writers, Writer
from lib.readers import readers, Reader
import lib.state_service as state


@click.group(chain=True)
@click.option("--state-service-name")
@click.option("--state-service-host", help="Redis server IP address")
@click.option("--state-service-port", help="Redis server port", default=6379)
def app(state_service_name, state_service_host, state_service_port):
    if (state_service_name or state_service_host) and not (state_service_name and state_service_host):
        raise click.BadParameter("You must specify both a name and a host for the state service")


@app.resultcallback()
def run(processors, state_service_name, state_service_host, state_service_port):
    state.configure(state_service_name, state_service_host, state_service_port)

    processor_instances = [p() for p in processors]

    _readers = list(filter(lambda o: isinstance(o, Reader), processor_instances))
    _writers = list(filter(lambda o: isinstance(o, Writer), processor_instances))

    if len(_readers) < 1:
        raise click.BadParameter("You must specify a reader")

    if len(_readers) > 1:
        raise click.BadParameter("You cannot specify multiple readers")

    if len(_writers) < 1:
        raise click.BadParameter("You must specify at least one writer")

    reader = _readers[0]

    # A stream should represent a full file!
    for stream in reader.read():
        for writer in _writers:
            writer.write(stream)


def build_commands():
    for writer in writers:
        app.add_command(writer)

    for reader in readers:
        app.add_command(reader)


if __name__ == "__main__":
    build_commands()
    app()
