import sys
import json
import click
import logging

from followthemoney import model
from followthemoney.namespace import Namespace
from followthemoney.cli.util import read_entity, write_object


@click.group(help="Utility for FollowTheMoney graph data")
def cli():
    fmt = '%(name)s [%(levelname)s] %(message)s'
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=fmt)


@cli.command('dump-model', help="Export the current schema model")
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
def dump_model(outfile):
    outfile.write(json.dumps(model.to_dict(), indent=2))


@cli.command('validate', help="Re-parse and validate the given data")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
def validate(infile, outfile):
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            clean = model.make_entity(entity.schema)
            clean.id = entity.id
            for (prop, value) in entity.itervalues():
                clean.add(prop, value)
            write_object(outfile, clean)
    except BrokenPipeError:
        raise click.Abort()


@cli.command('sign', help="Apply an HMAC signature to entity IDs")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('-s', '--signature', default=None, help='HMAC signature key')  # noqa
def sign(infile, outfile, signature):
    ns = Namespace(signature)
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            signed = ns.apply(entity)
            write_object(outfile, signed)
    except BrokenPipeError:
        raise click.Abort()


@cli.command(help="Format a stream of entities to make it readable")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
def pretty(infile):
    stdout = click.get_text_stream('stdout')
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            data = json.dumps(entity.to_dict(), indent=2)
            stdout.write(data + '\n')
    except BrokenPipeError:
        raise click.Abort()
