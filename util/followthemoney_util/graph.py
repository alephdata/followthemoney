import click
import networkx as nx
from networkx.readwrite.gexf import generate_gexf

from followthemoney.graph.export import CypherGraphExport
from followthemoney.graph.export import NXGraphExport
from followthemoney_util.cli import cli
from followthemoney_util.util import read_object


@cli.command('export-gexf', help="Export to GEXF (Gephi) format")
def export_gexf():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    graph = nx.MultiDiGraph()
    exporter = NXGraphExport(graph)
    try:
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            exporter.write(entity)
    except BrokenPipeError:
        pass

    for line in generate_gexf(graph, prettyprint=False):
        stdout.write(line)


@cli.command('export-cypher', help="Export to Cypher script")
def export_cypher():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    exporter = CypherGraphExport(stdout)
    try:
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            exporter.write(entity)
    except BrokenPipeError:
        pass
