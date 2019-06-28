import json
import click
import logging
from banal import is_mapping

from followthemoney.namespace import Namespace
from followthemoney.dedupe import Recon, EntityLinker
from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity, write_object
from followthemoney_enrich import get_enricher, enricher_cache
from followthemoney_enrich.result import Result

log = logging.getLogger(__name__)
NS = Namespace(None)
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


def read_result(stream):
    line = stream.readline()
    if not line:
        return
    data = json.loads(line)
    if is_mapping(data) and 'enricher' in data:
        enricher = load_enricher(data.get('enricher'))
        return Result.from_dict(enricher, data)
    return data


@cli.command('enrich', help="Find matching entities remotely")
@click.argument('enricher')
def enrich(enricher):
    enricher = load_enricher(enricher)
    try:
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            entity = read_entity(stdin)
            if entity is None:
                break
            for result in enricher.enrich_entity(entity):
                write_object(stdout, result)
    except BrokenPipeError:
        raise click.Abort()
    finally:
        enricher.close()


@cli.command('expand', help="Expand enriched entities")
@click.argument('enricher')
def expand(enricher):
    enricher = load_enricher(enricher)
    try:
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            entity = read_entity(stdin)
            if entity is None:
                break
            result = enricher.expand_entity(entity)
            write_object(stdout, result)
    except BrokenPipeError:
        raise click.Abort()
    finally:
        enricher.close()





@cli.command('auto-match', help="Generate result matches based purely on score")  # noqa
@click.option('-t', '--threshold', type=float, default=0.8)
def auto_match(threshold):
    try:
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            result = read_result(stdin)
            if result is None:
                break
            if result.score > threshold:
                recon = Recon(result.subject, result.candidate, Recon.MATCH)
                write_object(stdout, recon)
    except BrokenPipeError:
        raise click.Abort()


@cli.command('apply-recon', help="Apply matches from a recon file")  # noqa
@click.option('-r', '--recon', type=click.File('r'), required=True)  # noqa
def apply_recon(recon):
    try:
        linker = EntityLinker()
        for recon in Recon.from_file(recon):
            if recon.judgement == Recon.MATCH:
                linker.add(recon.subject, recon.canonical)
        log.info("Linker: %s clusters.", len(linker.clusters))
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            entity = read_entity(stdin)
            if entity is None:
                break
            entity = NS.apply(entity)
            outgoing = linker.apply(entity)
            if outgoing.id != entity.id:
                outgoing.add('sameAs', entity.id, quiet=True)
            write_object(stdout, outgoing)
    except BrokenPipeError:
        raise click.Abort()


@cli.command('filter-results', help="Filter results to those matching a recon")  # noqa
@click.option('-r', '--recon', type=click.File('r'), required=True)  # noqa
def filter_results(recon):
    try:
        matches = set()
        for recon in Recon.from_file(recon):
            if recon.judgement == Recon.MATCH:
                matches.add(recon.subject)
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            result = read_result(stdin)
            if result is None:
                break
            if result.candidate is None:
                continue
            candidate = NS.apply(result.candidate)
            if candidate.id in matches:
                write_object(stdout, result)
    except BrokenPipeError:
        raise click.Abort()


@cli.command('result-entities', help="Unnests results into entities")
def result_entities():
    try:
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            result = read_result(stdin)
            if result is None:
                break
            for entity in result.entities:
                write_object(stdout, entity)
    except BrokenPipeError:
        raise click.Abort()
