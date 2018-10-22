import click
from banal import ensure_list

from followthemoney_util.cli import cli
from followthemoney_util.util import read_object, write_object
from followthemoney_enrich import get_enricher


def load_enricher(enricher):
    clazz = get_enricher(enricher)
    if clazz is None:
        raise click.BadParameter("Unknown enricher: %s" % enricher)
    enricher = clazz()
    return enricher


@cli.command('enrich', help="Find matching entities remotely")
@click.argument('enricher')
def enrich(enricher):
    enricher = load_enricher(enricher)
    try:
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            has_result = False
            for result in enricher.enrich_entity(entity):
                has_result = True
                write_object(stdout, result)
            if not has_result:
                # emit the original entity anyways for streaming.
                result = enricher.make_result(entity)
                write_object(stdout, result)
    except BrokenPipeError:
        pass


@cli.command('expand', help="Expand enriched entities")
@click.argument('enricher')
def expand(enricher):
    enricher = load_enricher(enricher)
    try:
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            result = enricher.expand_entity(entity)
            write_object(stdout, result)
    except BrokenPipeError:
        pass


@cli.command('result-entities', help="Unnests results into entities")
def result_entities():
    try:
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            result = read_object(stdin)
            if result is None:
                break
            for entity in ensure_list(result.get('entities')):
                write_object(stdout, entity)
    except BrokenPipeError:
        pass
