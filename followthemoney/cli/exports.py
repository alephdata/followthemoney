import click

from followthemoney.cli.cli import cli
from followthemoney.cli.util import export_stream
from followthemoney.export.csv import CSVExporter
from followthemoney.export.rdf import RDFExporter
from followthemoney.export.excel import ExcelExporter
from followthemoney.export.graph import edge_types, DEFAULT_EDGE_TYPES
from followthemoney.export.graph import NXGraphExporter
from followthemoney.export.neo4j import Neo4JCSVExporter
from followthemoney.export.neo4j import CypherGraphExporter


@cli.command('export-csv', help="Export to CSV")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outdir', type=click.Path(file_okay=False, writable=True), default='.', help="output directory")  # noqa
def export_csv(infile, outdir):
    exporter = CSVExporter(outdir)
    export_stream(exporter, infile)


@cli.command('export-excel', help="Export to Excel")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.Path(dir_okay=False, writable=True), required=True)  # noqa
def export_excel(infile, outfile):
    exporter = ExcelExporter(outfile)
    export_stream(exporter, infile)


@cli.command('export-rdf', help="Export to RDF NTriples")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('--qualified/--unqualified', is_flag=True, default=True, help='Generate full predicates')  # noqa
def export_rdf(infile, outfile, qualified=True):
    exporter = RDFExporter(outfile, qualified=qualified)
    export_stream(exporter, infile)


@cli.command('export-gexf', help="Export to GEXF (Gephi) format")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('-e', '--edge-types', type=click.Choice(edge_types()),
              multiple=True, default=DEFAULT_EDGE_TYPES,
              help="Property types to be reified into graph edges.")
def export_gexf(infile, outfile, edge_types):
    exporter = NXGraphExporter(outfile, edge_types=edge_types)
    export_stream(exporter, infile)


@cli.command('export-cypher', help="Export to Cypher script")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('-e', '--edge-types', type=click.Choice(edge_types()),
              multiple=True, default=DEFAULT_EDGE_TYPES,
              help="Property types to be reified into graph edges.")
def export_cypher(infile, outfile, edge_types):
    exporter = CypherGraphExporter(outfile, edge_types=edge_types)
    export_stream(exporter, infile)


@cli.command('export-neo4j-bulk', help="Export to Neo4J bulk import")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outdir', type=click.Path(file_okay=False, writable=True), default='.', help="output directory")  # noqa
@click.option('-e', '--edge-types', type=click.Choice(edge_types()),
              multiple=True, default=DEFAULT_EDGE_TYPES,
              help="Property types to be reified into graph edges.")
def export_neo4j_bulk(infile, outdir, edge_types):
    exporter = Neo4JCSVExporter(outdir, edge_types=edge_types)
    export_stream(exporter, infile)
