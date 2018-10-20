import json
import click
from rdflib import Graph

from followthemoney import model
from followthemoney_util.cli import cli


@cli.command('export-rdf', help="Export to RDF NTriples")
def export_rdf():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    try:
        while True:
            line = stdin.readline()
            if not line:
                break
            entity = model.get_proxy(json.loads(line))
            graph = Graph()
            for link in entity.links:
                triple = link.rdf()
                if triple is None:
                    continue
                graph.add(triple)
            nt = graph.serialize(format='nt').strip()
            stdout.write(nt.decode('utf-8') + '\n')
    except BrokenPipeError:
        pass
