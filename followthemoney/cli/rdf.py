import click
import logging
from rdflib import Graph

from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity

log = logging.getLogger(__name__)


@cli.command('export-rdf', help="Export to RDF NTriples")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('--external', is_flag=True, default=True, help='Generate full predicates')  # noqa
def export_rdf(infile, outfile, external=True):
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            graph = Graph()
            for triple in entity.triples(external=external):
                graph.add(triple)
            try:
                nt = graph.serialize(format='nt').strip()
                outfile.write(nt.decode('utf-8') + '\n')
            except Exception:
                log.exception("Failed to serialize ntriples.")
    except BrokenPipeError:
        raise click.Abort()
