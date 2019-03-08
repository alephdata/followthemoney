import os

import click

from followthemoney_util.cli import cli
from followthemoney_util.util import read_object
from followthemoney.export.excel import get_workbook, write_entity


@cli.command('export-excel', help="Export to Excel")
@click.option('-f', '--filename', type=click.Path(),
              default='export.xlsx', help="output file path")
def export_excel(filename):
    stdin = click.get_text_stream('stdin')
    workbook = get_workbook()
    try:
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            write_entity(workbook, entity)
        workbook.save(filename)
    except BrokenPipeError:
        raise click.Abort()
