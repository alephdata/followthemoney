import click
from pathlib import Path
from typing import Dict

from followthemoney.proxy import EntityProxy
from followthemoney.namespace import Namespace
from followthemoney.cli.cli import cli
from followthemoney.cli.util import InPath, OutPath, path_entities
from followthemoney.cli.util import path_writer, write_entity


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
