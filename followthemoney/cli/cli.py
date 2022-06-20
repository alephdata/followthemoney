import sys
import json
import click
import logging
from pathlib import Path
from typing import Optional, TextIO
from banal import ensure_list

from followthemoney import model
from followthemoney.namespace import Namespace
from followthemoney.cli.util import InPath, OutPath, path_entities, read_entities
from followthemoney.cli.util import path_writer, write_entity
from followthemoney.proxy import EntityProxy


@click.group(help="Utility for FollowTheMoney graph data")
def cli() -> None:
    fmt = "%(name)s [%(levelname)s] %(message)s"
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=fmt)


@cli.command("dump-model", help="Export the current schema model")
@click.option("-o", "--outfile", type=click.File("w"), default="-")
def dump_model(outfile: TextIO) -> None:
    outfile.write(json.dumps(model.to_dict(), indent=2, sort_keys=True))


@cli.command("validate", help="Re-parse and validate the given data")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option("-o", "--outfile", type=OutPath, default="-")
def validate(infile: Path, outfile: Path) -> None:
    try:
        with path_writer(outfile) as outfh:
            for entity in path_entities(infile, EntityProxy, cleaned=False):
                clean = model.make_entity(entity.schema)
                clean.id = entity.id
                for (prop, value) in entity.itervalues():
                    clean.add(prop, value)
                write_entity(outfh, clean)
    except BrokenPipeError:
        raise click.Abort()


@cli.command("import-vis", help="Load a .VIS file and get entities")
@click.option("-i", "--infile", type=InPath, default="-")  # noqa
@click.option("-o", "--outfile", type=OutPath, default="-")  # noqa
def import_vis(infile: Path, outfile: Path) -> None:
    with path_writer(outfile) as outfh:
        with open(infile, "r") as infh:
            data = json.load(infh)
            if "entities" in data:
                entities = data.get("entities", data)
            if "layout" in data:
                entities = data.get("layout", {}).get("entities", data)
            for entity_data in ensure_list(entities):
                entity = EntityProxy.from_dict(model, entity_data)
                write_entity(outfh, entity)


@cli.command("sign", help="Apply a HMAC signature to entity IDs")
@click.option("-i", "--infile", type=InPath, default="-")  # noqa
@click.option("-o", "--outfile", type=OutPath, default="-")  # noqa
@click.option("-s", "--signature", default=None, help="HMAC signature key")  # noqa
def sign(infile: Path, outfile: Path, signature: Optional[str]) -> None:
    ns = Namespace(signature)
    try:
        with path_writer(outfile) as outfh:
            for entity in path_entities(infile, EntityProxy):
                signed = ns.apply(entity)
                write_entity(outfh, signed)
    except BrokenPipeError:
        raise click.Abort()


@cli.command(help="Format a stream of entities to make it readable")
@click.option("-i", "--infile", type=InPath, default="-")  # noqa
def pretty(infile: Path) -> None:
    stdout = click.get_text_stream("stdout")
    try:
        for entity in path_entities(infile, EntityProxy):
            data = json.dumps(entity.to_dict(), indent=2)
            stdout.write(data + "\n")
    except BrokenPipeError:
        raise click.Abort()
