import click
from rdflib import Graph

from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity


@cli.command('export-rdf', help="Export to RDF NTriples")
def export_rdf():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    try:
        while True:
            entity = read_entity(stdin)
            if entity is None:
                break
            graph = Graph()
            for triple in entity.triples:
                graph.add(triple)
            nt = graph.serialize(format='nt').strip()
            stdout.write(nt.decode('utf-8') + '\n')
    except BrokenPipeError:
        raise click.Abort()
