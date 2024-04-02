import sys
import click
import orjson
import logging
from pathlib import Path
from typing import Optional, BinaryIO, List, Any, Dict
from banal import ensure_list

from followthemoney import model
from followthemoney.namespace import Namespace
from followthemoney.cli.util import InPath, OutPath, path_entities
from followthemoney.cli.util import path_writer, write_entity
from followthemoney.proxy import EntityProxy


@click.group(help="Utility for FollowTheMoney graph data")
def cli() -> None:
    fmt = "%(name)s [%(levelname)s] %(message)s"
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=fmt)


@cli.command("dump-model", help="Export the current schema model")
@click.option("-o", "--outfile", type=click.File("wb"), default="-")
def dump_model(outfile: BinaryIO) -> None:
    f = orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS
    outfile.write(orjson.dumps(model.to_dict(), option=f))


@cli.command("validate", help="Re-parse and validate the given data")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option("-o", "--outfile", type=OutPath, default="-")
def validate(infile: Path, outfile: Path) -> None:
    try:
        with path_writer(outfile) as outfh:
            for entity in path_entities(infile, EntityProxy, cleaned=False):
                clean = model.make_entity(entity.schema)
                clean.id = entity.id
                for prop, value in entity.itervalues():
                    clean.add(prop, value)
                write_entity(outfh, clean)
    except BrokenPipeError:
        raise click.Abort()


@cli.command("import-vis", help="Load a .VIS file and get entities")
@click.option("-i", "--infile", type=InPath, default="-")  # noqa
@click.option("-o", "--outfile", type=OutPath, default="-")  # noqa
def import_vis(infile: Path, outfile: Path) -> None:
    with path_writer(outfile) as outfh:
        with open(infile, "rb") as infh:
            data: Dict[str, Any] = orjson.loads(infh.read())
            if "entities" in data:
                entities: List[Dict[str, Any]] = data.get("entities", data)
            elif "layout" in data:
                entities = data.get("layout", {}).get("entities", data)
            else:
                raise click.ClickException("No entities found in VIS file")
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
    stdout = click.get_binary_stream("stdout")
    try:
        f = orjson.OPT_INDENT_2 | orjson.OPT_APPEND_NEWLINE
        for entity in path_entities(infile, EntityProxy):
            data = orjson.dumps(entity.to_dict(), option=f)
            stdout.write(data)
    except BrokenPipeError:
        raise click.Abort()
