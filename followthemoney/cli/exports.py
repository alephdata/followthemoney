import click
from typing import List, TextIO, Generator
from pathlib import Path
from contextlib import contextmanager

from followthemoney.cli.cli import cli
from followthemoney.cli.util import InPath, OutPath, export_stream
from followthemoney.export.csv import CSVExporter
from followthemoney.export.rdf import RDFExporter
from followthemoney.export.excel import ExcelExporter
from followthemoney.export.graph import edge_types, DEFAULT_EDGE_TYPES
from followthemoney.export.graph import NXGraphExporter
from followthemoney.export.neo4j import Neo4JCSVExporter
from followthemoney.export.neo4j import CypherGraphExporter


@contextmanager
def text_out(path: Path) -> Generator[TextIO, None, None]:
    if str(path) == "-":
        yield click.get_text_stream("stdout")
        return
    with open(path, "w") as fh:
        yield fh


@cli.command("export-csv", help="Export to CSV")
@click.option("-i", "--infile", type=InPath, default="-")  # noqa
@click.option(
    "-o",
    "--outdir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=".",
    help="output directory",
)
def export_csv(infile: Path, outdir: Path) -> None:
    exporter = CSVExporter(outdir)
    export_stream(exporter, infile)


@cli.command("export-excel", help="Export to Excel")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option(
    "-o",
    "--outfile",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    required=True,
)
def export_excel(infile: Path, outfile: Path) -> None:
    exporter = ExcelExporter(outfile)
    export_stream(exporter, infile)


@cli.command("export-rdf", help="Export to RDF NTriples")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option("-o", "--outfile", type=OutPath, default="-")
@click.option(
    "--qualified/--unqualified",
    is_flag=True,
    default=True,
    help="Generate full predicates",
)
def export_rdf(infile: Path, outfile: Path, qualified: bool = True) -> None:
    with text_out(outfile) as fh:
        exporter = RDFExporter(fh, qualified=qualified)
        export_stream(exporter, infile)


@cli.command("export-gexf", help="Export to GEXF (Gephi) format")
@click.option("-i", "--infile", type=InPath, default="-")
@click.option("-o", "--outfile", type=OutPath, default="-")
@click.option(
    "-e",
    "--edge-types",
    type=click.Choice(edge_types()),
    multiple=True,
    default=DEFAULT_EDGE_TYPES,
    help="Property types to be reified into graph edges.",
)
def export_gexf(infile: Path, outfile: Path, edge_types: List[str]) -> None:
    with text_out(outfile) as fh:
        exporter = NXGraphExporter(fh, edge_types=edge_types)
        export_stream(exporter, infile)


@cli.command("export-cypher", help="Export to Cypher script")
@click.option("-i", "--infile", type=InPath, default="-")  # noqa
@click.option("-o", "--outfile", type=OutPath, default="-")  # noqa
@click.option(
    "-e",
    "--edge-types",
    type=click.Choice(edge_types()),
    multiple=True,
    default=DEFAULT_EDGE_TYPES,
    help="Property types to be reified into graph edges.",
)
def export_cypher(infile: Path, outfile: Path, edge_types: List[str]) -> None:
    with text_out(outfile) as fh:
        exporter = CypherGraphExporter(fh, edge_types=edge_types)
        export_stream(exporter, infile)


@cli.command("export-neo4j-bulk", help="Export to Neo4J bulk import")
@click.option("-i", "--infile", type=InPath, default="-")  # noqa
@click.option(
    "-o",
    "--outdir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    required=True,
    help="Output directory for Neo4J import script",
)
@click.option(
    "-e",
    "--edge-types",
    type=click.Choice(edge_types()),
    multiple=True,
    default=DEFAULT_EDGE_TYPES,
    help="Property types to be reified into graph edges.",
)
def export_neo4j_bulk(infile: Path, outdir: Path, edge_types: List[str]) -> None:
    exporter = Neo4JCSVExporter(outdir, edge_types=edge_types)
    export_stream(exporter, infile)
