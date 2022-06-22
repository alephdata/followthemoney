import click
from pathlib import Path
from typing import Dict, Optional, Type

from followthemoney.proxy import EntityProxy, E
from followthemoney.namespace import Namespace
from followthemoney.cli.cli import cli
from followthemoney.cli.util import InPath, OutPath, path_entities
from followthemoney.cli.util import path_writer, write_entity


def sorted_aggregate(path: Path, outpath: Path, entity_type: Type[E]) -> None:
    """Aggregate entities based on the premise that the fragements in the source
    stream are sorted by their ID."""
    entity: Optional[E] = None
    with path_writer(outpath) as outfh:
        for next_entity in path_entities(path, entity_type=entity_type):
            if entity is None:
                entity = next_entity
                continue
            if next_entity.id == entity.id:
                entity = entity.merge(next_entity)
                continue
            write_entity(outfh, entity)
            entity = next_entity

        if entity is not None:
            write_entity(outfh, entity)


@cli.command("aggregate", help="Aggregate multiple fragments of entities")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option("-o", "--outfile", type=OutPath, default="-")
def aggregate(infile: Path, outfile: Path) -> None:
    buffer: Dict[str, EntityProxy] = {}
    namespace = Namespace(None)
    try:
        with path_writer(outfile) as outfh:
            for entity in path_entities(infile, EntityProxy):
                entity = namespace.apply(entity)
                if entity.id in buffer:
                    buffer[entity.id].merge(entity)
                else:
                    buffer[entity.id] = entity

            for entity in buffer.values():
                write_entity(outfh, entity)
    except BrokenPipeError:
        raise click.Abort()


@cli.command("sorted-aggregate", help="Aggregate sorted fragments of entities")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option("-o", "--outfile", type=OutPath, default="-")
def sorted_aggregate_(infile: Path, outfile: Path) -> None:
    sorted_aggregate(infile, outfile, EntityProxy)
