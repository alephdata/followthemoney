import sys
import json
import click
import logging

from followthemoney_util.util import read_object


@click.group(help="Command-line utility for FollowTheMoney graph data")
def cli():
    fmt = '%(name)s [%(levelname)s] %(message)s'
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=fmt)


@cli.command(help="Format a stream of entities to make it readable")
def pretty():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    try:
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            data = json.dumps(entity.to_dict(), indent=2)
            stdout.write(data + '\n')
    except BrokenPipeError:
        pass
