import click
import logging

from followthemoney import model
from followthemoney.dedupe import Linker, Match
from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity, write_object

log = logging.getLogger(__name__)


@cli.command('link', help="Apply matches from a deduplication match file")  # noqa
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('-m', '--matches', type=click.File('r'), required=True)  # noqa
def link(infile, outfile, matches):
    try:
        linker = Linker(model)
        for match in Match.from_file(model, matches):
            linker.add(match)
        log.info("Linker: %s clusters.", len(linker.lookup))
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            entity = linker.apply(entity)
            write_object(outfile, entity)
    except BrokenPipeError:
        raise click.Abort()


@cli.command('match-decide', help="Generate match decisions based purely on score")  # noqa
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('-t', '--threshold', type=float, default=0.8)
def match_decide(infile, outfile, threshold):
    try:
        for match in Match.from_file(model, infile):
            if match.decision is None:
                if match.score is not None and match.score > threshold:
                    match.decision = True
            write_object(outfile, match)
    except BrokenPipeError:
        raise click.Abort()


@cli.command('match-entities', help="Unnests matches into entities")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('-a', '--all', is_flag=True, default=False, help='Unnest non-positive matches')  # noqa
def match_entities(infile, outfile, all):
    try:
        for match in Match.from_file(model, infile):
            if not all and match.decision is not True:
                continue
            if match.canonical is not None:
                write_object(outfile, match.canonical)
            if match.entity is not None:
                write_object(outfile, match.entity)
    except BrokenPipeError:
        raise click.Abort()
