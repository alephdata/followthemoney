import click
import logging

from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity, write_object
from followthemoney_enrich import get_enricher, enricher_cache

log = logging.getLogger(__name__)
ENRICHERS = {}


def load_enricher(name):
    if name not in ENRICHERS:
        clazz = get_enricher(name)
        if clazz is None:
            raise click.BadParameter("Unknown enricher: %s" % name)
        enricher = clazz()
        enricher.cache = enricher_cache()
        ENRICHERS[name] = enricher
    return ENRICHERS[name]


@cli.command('enrich', help="Find matching entities remotely")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.argument('enricher')
def enrich(infile, outfile, enricher):
    enricher = load_enricher(enricher)
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            for match in enricher.enrich_entity_raw(entity):
                write_object(outfile, match)
    except BrokenPipeError:
        raise click.Abort()


@cli.command('expand', help="Expand enriched entities")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.argument('enricher')
def expand(infile, outfile, enricher):
    enricher = load_enricher(enricher)
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            for entity in enricher.expand_entity(entity):
                write_object(outfile, entity)
    except BrokenPipeError:
        raise click.Abort()
