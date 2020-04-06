import click
import logging
from followthemoney.namespace import Namespace
from followthemoney.dedupe import Linker, Match

from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity, write_object

log = logging.getLogger(__name__)


@cli.command('link', help="Apply matches from a deduplication match file")  # noqa
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('-m', '--matches', type=click.File('r'), required=True)  # noqa
@click.option('-s', '--signature', default=None, help='HMAC signature key')  # noqa
def link(infile, outfile, matches, signature):
    try:
        namespace = Namespace(name=signature)
        linker = Linker()
        for match in Match.from_file(matches):
            linker.add(match)
        log.info("Linker: %s clusters.", len(linker.lookup))
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            entity = linker.apply(entity)
            entity = namespace.apply(entity)
            write_object(outfile, entity)
    except BrokenPipeError:
        raise click.Abort()
