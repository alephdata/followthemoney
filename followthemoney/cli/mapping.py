import sys
import click
from pathlib import Path
from banal import keys_values
from typing import Generator, List, TextIO, Tuple
from contextlib import contextmanager

from followthemoney import model
from followthemoney.namespace import Namespace
from followthemoney.mapping.query import QueryMapping
from followthemoney.mapping.csv import CSVSource
from followthemoney.cli.cli import cli
from followthemoney.cli.util import InPath, OutPath, load_mapping_file
from followthemoney.cli.util import path_writer, write_entity


@contextmanager
def input_file(path: Path) -> Generator[TextIO, None, None]:
    if str(path) == "-":
        yield sys.stdin
        return
    with open(path, "r") as fh:
        yield fh


@cli.command("map", help="Execute a mapping file and emit objects")
@click.option("-o", "--outfile", type=OutPath, default="-")
@click.option(
    "--sign/--no-sign",
    is_flag=True,
    default=True,
    help="Apply HMAC signature",
)
@click.argument("mapping_yaml", type=click.Path(exists=True, path_type=Path))
def run_mapping(outfile: Path, mapping_yaml: Path, sign: bool = True) -> None:
    config = load_mapping_file(mapping_yaml)
    try:
        with path_writer(outfile) as outfh:
            for dataset, meta in config.items():
                ns = Namespace(dataset)
                for mapping in keys_values(meta, "queries", "query"):
                    entities = model.map_entities(mapping, key_prefix=dataset)
                    for entity in entities:
                        if sign:
                            entity = ns.apply(entity)
                        write_entity(outfh, entity)
    except BrokenPipeError:
        raise click.Abort()
    except Exception as exc:
        raise click.ClickException(str(exc))


@cli.command("map-csv", help="Map CSV data from stdin and emit objects")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option("-o", "--outfile", type=OutPath, default="-")
@click.option(
    "--sign/--no-sign", is_flag=True, default=True, help="Apply HMAC signature"
)
@click.argument("mapping_yaml", type=click.Path(exists=True, path_type=Path))
def stream_mapping(
    infile: Path, outfile: Path, mapping_yaml: Path, sign: bool = True
) -> None:
    queries: List[Tuple[str, QueryMapping]] = []
    config = load_mapping_file(mapping_yaml)
    for dataset, meta in config.items():
        for data in keys_values(meta, "queries", "query"):
            data.pop("database", None)
            data["csv_url"] = "/dev/null"
            query = model.make_mapping(data, key_prefix=dataset)
            queries.append((dataset, query))

    try:
        with path_writer(outfile) as outfh:
            with input_file(infile) as fh:
                for record in CSVSource.read_csv(fh):
                    for (dataset, query) in queries:
                        ns = Namespace(dataset)
                        if query.source.check_filters(record):  # type: ignore
                            entities = query.map(record)
                            for entity in entities.values():
                                if sign:
                                    entity = ns.apply(entity)
                                write_entity(outfh, entity)
    except BrokenPipeError:
        raise click.Abort()
