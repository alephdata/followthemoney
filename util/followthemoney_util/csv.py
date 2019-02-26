import csv
import os

import click

from followthemoney_util.cli import cli
from followthemoney_util.util import read_object


def _get_csv_handler(outdir, schema, handlers):
    fh = handlers.get(schema.name)
    if fh is None:
        name = "{0}.csv".format(schema.plural)
        path = os.path.join(outdir, name)
        handlers[schema.name] = fh = open(path, 'w')
        fieldnames = [prop.label for prop in schema.sorted_properties]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
    return fh


def _write_entity(fh, entity):
    fieldnames = [prop.label for prop in entity.schema.sorted_properties]
    writer = csv.DictWriter(fh, fieldnames=fieldnames)
    prop_dict = {}
    for prop in entity.schema.sorted_properties:
        prop_dict[prop.label] = prop.type.join(entity.get(prop))
    writer.writerow(prop_dict)


@cli.command('export-csv', help="Export to CSV")
@click.option('--outdir', type=click.Path(exists=True), default='.',
              help="output directory")
def export_csv(outdir):
    stdin = click.get_text_stream('stdin')
    handlers = {}
    try:
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            fh = _get_csv_handler(outdir, entity.schema, handlers)
            _write_entity(fh, entity)
    except BrokenPipeError:
        raise click.Abort()
    finally:
        for fh in handlers.values():
            fh.close()
