import os

import click

from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity
from followthemoney.export.csv import write_entity, write_headers


def _get_csv_handler(outdir, schema, handlers):
    fh = handlers.get(schema.name)
    if fh is None:
        name = "{0}.csv".format(schema.name)
        path = os.path.join(outdir, name)
        handlers[schema.name] = fh = open(path, 'w')
        write_headers(fh, schema)
    return fh


@cli.command('export-csv', help="Export to CSV")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outdir', type=click.Path(exists=True, file_okay=False, writable=True), default='.', help="output directory")  # noqa
def export_csv(infile, outdir):
    handlers = {}
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            fh = _get_csv_handler(outdir, entity.schema, handlers)
            write_entity(fh, entity)
    except BrokenPipeError:
        raise click.Abort()
    finally:
        for fh in handlers.values():
            fh.close()
