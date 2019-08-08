import click
import networkx as nx
from networkx.readwrite.gexf import generate_gexf

from followthemoney.export.graph import CypherGraphExport
from followthemoney.export.graph import NXGraphExport
from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity


@cli.command('export-gexf', help="Export to GEXF (Gephi) format")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
def export_gexf(infile, outfile):
    graph = nx.MultiDiGraph()
    exporter = NXGraphExport(graph)
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            exporter.write(entity)
    except BrokenPipeError:
        raise click.Abort()

    for line in generate_gexf(graph, prettyprint=False):
        outfile.write(line)


@cli.command('export-cypher', help="Export to Cypher script")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
def export_cypher(infile, outfile):
    exporter = CypherGraphExport(outfile)
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            exporter.write(entity)
    except BrokenPipeError:
        raise click.Abort()
