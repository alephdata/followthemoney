import os

import click

from followthemoney_util.cli import cli
from followthemoney_util.util import read_object
from followthemoney.export.excel import get_workbook, get_sheet, write_entity


@cli.command('export-excel', help="Export to Excel")
@click.option('--filename', default='export.xlsx',
              help="name of the excel file")
@click.option('--outdir', type=click.Path(exists=True), default='.',
              help="output directory")
def export_excel(filename, outdir):
    stdin = click.get_text_stream('stdin')
    workbook = get_workbook()
    try:
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            sheet = get_sheet(entity.schema, workbook)
            write_entity(sheet, entity)
    except BrokenPipeError:
        raise click.Abort()
    finally:
        path = os.path.join(outdir, filename)
        workbook.save(path)
