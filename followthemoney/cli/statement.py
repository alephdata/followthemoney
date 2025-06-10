import click
from pathlib import Path
from typing import Generator, List


from followthemoney.cli.cli import cli
from followthemoney.cli.util import InPath, OutPath
from followthemoney.cli.util import path_entities, write_entity, path_writer
from followthemoney.dataset import Dataset, DefaultDataset
from followthemoney.statement import Statement, StatementEntity
from followthemoney.statement import FORMATS, CSV
from followthemoney.statement import write_statements
from followthemoney.statement import read_path_statements


@cli.command("statements", help="Export entities to statements")
@click.argument("path", type=InPath)
@click.option("-o", "--outpath", type=OutPath, default="-")
@click.option("-d", "--dataset", type=str, required=True)
@click.option("-f", "--format", type=click.Choice(FORMATS), default=CSV)
def entity_statements(path: Path, outpath: Path, dataset: str, format: str) -> None:
    def make_statements() -> Generator[Statement, None, None]:
        for entity in path_entities(path, StatementEntity):
            yield from Statement.from_entity(entity, dataset=dataset)

    with path_writer(outpath) as outfh:
        write_statements(outfh, format, make_statements())


@cli.command("format-statements", help="Convert entity data formats")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option("-o", "--outpath", type=OutPath, default="-")
@click.option("-f", "--in-format", type=click.Choice(FORMATS), default=CSV)
@click.option("-x", "--out-format", type=click.Choice(FORMATS), default=CSV)
def format_statements(
    infile: Path, outpath: Path, in_format: str, out_format: str
) -> None:
    statements = read_path_statements(infile, format=in_format)
    with path_writer(outpath) as outfh:
        write_statements(outfh, out_format, statements)


@cli.command("aggregate-statements", help="Roll up statements into entities")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option("-o", "--outpath", type=OutPath, default="-")
@click.option("-d", "--dataset", type=str, default=DefaultDataset.name)
@click.option("-f", "--format", type=click.Choice(FORMATS), default=CSV)
def statements_aggregate(
    infile: Path, outpath: Path, dataset: str, format: str
) -> None:
    dataset_ = Dataset.make({"name": dataset, "title": dataset})
    with path_writer(outpath) as outfh:
        statements: List[Statement] = []
        for stmt in read_path_statements(infile, format=format):
            if len(statements) and statements[0].canonical_id != stmt.canonical_id:
                entity = StatementEntity.from_statements(dataset_, statements)
                write_entity(outfh, entity)
                statements = []
            statements.append(stmt)
        if len(statements):
            entity = StatementEntity.from_statements(dataset_, statements)
            write_entity(outfh, entity)
