import click
from followthemoney.namespace import Namespace

from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity, write_object


@cli.command('aggregate', help="Aggregate multiple fragments of entities")
def aggregate():
    buffer = {}
    namespace = Namespace(None)
    try:
        stdin = click.get_text_stream('stdin')
        while True:
            entity = read_entity(stdin)
            if entity is None:
                break
            entity = namespace.apply(entity)
            if entity.id in buffer:
                buffer[entity.id].merge(entity)
            else:
                buffer[entity.id] = entity

        stdout = click.get_text_stream('stdout')
        for entity in buffer.values():
            write_object(stdout, entity)
    except BrokenPipeError:
        raise click.Abort()
