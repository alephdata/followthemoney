import click
import networkx as nx
from networkx.readwrite.gexf import generate_gexf

from followthemoney_util.cli import cli
from followthemoney_util.util import read_object


@cli.command('export-gexf', help="Export to GEXF (Gephi) format")
def export_gexf():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    graph = nx.MultiDiGraph()
    try:
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            for link in entity.links:
                link.to_digraph(graph)
    except BrokenPipeError:
        pass

    for line in generate_gexf(graph, prettyprint=False):
        stdout.write(line)
