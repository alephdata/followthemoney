import click

from followthemoney.dedupe import Recon, EntityLinker
from followthemoney_util.cli import cli
from followthemoney_util.util import read_object, write_object


@cli.command('auto-match', help="Generate result matches based purely on score")  # noqa
@click.option('-t', '--threshold', type=float, default=0.8)
def auto_match(threshold):
    try:
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            result = read_object(stdin)
            if result is None:
                break
            if result.score > threshold:
                recon = Recon(result.subject, result.candidate, Recon.MATCH)
                write_object(stdout, recon)
    except BrokenPipeError:
        pass


@cli.command('apply-recon', help="Apply matches from a recon file")  # noqa
@click.option('-r', '--recon', type=click.File('r'), required=True)  # noqa
def auto_match(recon):
    try:
        linker = EntityLinker()
        for recon in Recon.from_file(recon):
            if recon.judgement == Recon.MATCH:
                linker.add(recon.subject, recon.canonical)
        stdin = click.get_text_stream('stdin')
        stdout = click.get_text_stream('stdout')
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            entity = linker.apply(entity)
            write_object(stdout, entity)
    except BrokenPipeError:
        pass


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
            result = read_object(stdin)
            if result is None:
                break
            if result.candidate is None:
                continue
            if result.candidate.id in matches:
                write_object(stdout, result)
    except BrokenPipeError:
        pass
