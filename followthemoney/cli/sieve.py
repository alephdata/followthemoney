import click

from followthemoney import model
from followthemoney.types import registry
from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity, write_object


def sieve_entity(entity, schemata, properties, types):
    for schema in schemata:
        if entity.schema.is_a(schema):
            return None
    for prop in entity.iterprops():
        if prop.name in properties or prop.qname in properties:
            entity.pop(prop, quiet=True)
        elif prop.type.name in types:
            entity.pop(prop, quiet=True)
    return entity


@cli.command('sieve', help="Filter out parts of entities.")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('-s', '--schema', type=click.Choice(model.schemata.keys()), multiple=True, help="Filter out the given schemata.")  # noqa
@click.option('-p', '--property', multiple=True, help="Filter out the given property names.")  # noqa
@click.option('-t', '--type', type=click.Choice([t.name for t in registry.types]), multiple=True, help="Filter out the given property types.")  # noqa
def sieve(infile, outfile, schema, property, type):
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            entity = sieve_entity(entity, schema, property, type)
            if entity is not None:
                write_object(outfile, entity)
    except BrokenPipeError:
        raise click.Abort()
