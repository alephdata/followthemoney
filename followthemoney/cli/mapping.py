import click
from banal import keys_values
from typing import List, Tuple

from followthemoney import model
from followthemoney.namespace import Namespace
from followthemoney.mapping.query import QueryMapping
from followthemoney.mapping.csv import CSVSource
from followthemoney.cli.cli import cli
from followthemoney.cli.util import write_object, load_mapping_file


@cli.command("map", help="Execute a mapping file and emit objects")
@click.option("-o", "--outfile", type=click.File("w"), default="-")  # noqa
@click.option(
    "--sign/--no-sign", is_flag=True, default=True, help="Apply HMAC signature"
)  # noqa
@click.argument("mapping_yaml", type=click.Path(exists=True))
def run_mapping(outfile, mapping_yaml, sign=True):
    config = load_mapping_file(mapping_yaml)
    try:
        for dataset, meta in config.items():
            ns = Namespace(dataset)
            for mapping in keys_values(meta, "queries", "query"):
                entities = model.map_entities(mapping, key_prefix=dataset)
                for entity in entities:
                    if sign:
                        entity = ns.apply(entity)
                    write_object(outfile, entity)
    except BrokenPipeError:
        raise click.Abort()
    except Exception as exc:
        raise click.ClickException(str(exc))


@cli.command("map-csv", help="Map CSV data from stdin and emit objects")
@click.option("-i", "--infile", type=click.File("r"), default="-")  # noqa
@click.option("-o", "--outfile", type=click.File("w"), default="-")  # noqa
@click.option(
    "--sign/--no-sign", is_flag=True, default=True, help="Apply HMAC signature"
)  # noqa
@click.argument("mapping_yaml", type=click.Path(exists=True))
def stream_mapping(infile, outfile, mapping_yaml, sign=True):
    queries: List[Tuple[str, QueryMapping]] = []
    config = load_mapping_file(mapping_yaml)
    for dataset, meta in config.items():
        for data in keys_values(meta, "queries", "query"):
            data.pop("database", None)
            data["csv_url"] = "/dev/null"
            query = model.make_mapping(data, key_prefix=dataset)
            queries.append((dataset, query))

    try:
        for record in CSVSource.read_csv(infile):
            for (dataset, query) in queries:
                ns = Namespace(dataset)
                if query.source.check_filters(record):
                    entities = query.map(record)
                    for entity in entities.values():
                        if sign:
                            entity = ns.apply(entity)
                        write_object(outfile, entity)
    except BrokenPipeError:
        raise click.Abort()
