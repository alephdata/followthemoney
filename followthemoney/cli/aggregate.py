import click
import logging
from followthemoney.namespace import Namespace

from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity, write_object

log = logging.getLogger(__name__)


@cli.command('aggregate', help="Aggregate multiple fragments of entities")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
def aggregate(infile, outfile):
    buffer = {}
    namespace = Namespace(None)
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            entity = namespace.apply(entity)
            if entity.id in buffer:
                buffer[entity.id].merge(entity)
            else:
                buffer[entity.id] = entity

        for entity in buffer.values():
            write_object(outfile, entity)
    except BrokenPipeError:
        raise click.Abort()
