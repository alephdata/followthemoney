import click
from rdflib import Graph

from followthemoney_util.cli import cli
from followthemoney_util.util import read_object


@cli.command('export-rdf', help="Export to RDF NTriples")
def export_rdf():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    try:
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            graph = Graph()
            for triple in entity.triples:
                graph.add(triple)
            nt = graph.serialize(format='nt').strip()
            stdout.write(nt.decode('utf-8') + '\n')
    except BrokenPipeError:
        pass
