import os

import click

from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity
from followthemoney.export.csv import write_entity, write_headers


def _get_csv_handler(outdir, schema, handlers):
    fh = handlers.get(schema.name)
    if fh is None:
        name = "{0}.csv".format(schema.plural)
        path = os.path.join(outdir, name)
        handlers[schema.name] = fh = open(path, 'w')
        write_headers(fh, schema)
    return fh


@cli.command('export-csv', help="Export to CSV")
@click.option('--outdir', type=click.Path(exists=True), default='.',
              help="output directory")
def export_csv(outdir):
    stdin = click.get_text_stream('stdin')
    handlers = {}
    try:
        while True:
            entity = read_entity(stdin)
            if entity is None:
                break
            fh = _get_csv_handler(outdir, entity.schema, handlers)
            write_entity(fh, entity)
    except BrokenPipeError:
        raise click.Abort()
    finally:
        for fh in handlers.values():
            fh.close()
