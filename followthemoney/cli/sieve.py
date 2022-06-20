import click
from pathlib import Path
from typing import Iterable, Optional

from followthemoney import model
from followthemoney.proxy import E, EntityProxy
from followthemoney.types import registry
from followthemoney.cli.cli import cli
from followthemoney.cli.util import InPath, OutPath, path_entities
from followthemoney.cli.util import path_writer, write_entity


def sieve_entity(
    entity: EntityProxy,
    schemata: Iterable[str],
    properties: Iterable[str],
    types: Iterable[str],
) -> Optional[EntityProxy]:
    for schema in schemata:
        if entity.schema.is_a(schema):
            return None
    for prop in entity.iterprops():
        if prop.name in properties or prop.qname in properties:
            entity.pop(prop, quiet=True)
        elif prop.type.name in types:
            entity.pop(prop, quiet=True)
    return entity


@cli.command("sieve", help="Filter out parts of entities.")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option("-o", "--outfile", type=OutPath, default="-")
@click.option(
    "-s",
    "--schema",
    type=click.Choice(list(model.schemata.keys())),
    multiple=True,
    help="Filter out the given schemata.",
)
@click.option(
    "-p",
    "--property",
    multiple=True,
    help="Filter out the given property names.",
)
@click.option(
    "-t",
    "--type",
    type=click.Choice([t.name for t in registry.types]),
    multiple=True,
    help="Filter out the given property types.",
)
def sieve(
    infile: Path,
    outfile: Path,
    schema: Iterable[str],
    property: Iterable[str],
    type: Iterable[str],
) -> None:
    try:
        with path_writer(outfile) as outfh:
            for entity in path_entities(infile, EntityProxy):
                sieved = sieve_entity(entity, schema, property, type)
                if sieved is not None:
                    write_entity(outfh, sieved)
    except BrokenPipeError:
        raise click.Abort()
