from config import logging

import click

from lib.readers import readers_list


@click.group()
def app():
    logging.info("Beginning of ingestion")


for reader in readers_list:
    app.add_command(readers_list[reader])


if __name__ == '__main__':
    app()
