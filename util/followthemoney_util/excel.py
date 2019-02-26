import os

import click
from openpyxl import Workbook

from followthemoney_util.cli import cli
from followthemoney_util.util import read_object


def _get_sheet(schema, workbook):
    try:
        sheet = workbook.get_sheet_by_name(name=schema.plural)
    except KeyError:
        sheet = workbook.create_sheet(title=schema.plural)
        fieldnames = [prop.label for prop in schema.sorted_properties]
        sheet.append(fieldnames)
    return sheet


def _write_entity(sheet, entity):
    prop_dict = {}
    for prop in entity.schema.sorted_properties:
        prop_dict[prop.label] = prop.type.join(entity.get(prop))
    sheet.append(list(prop_dict.values()))


@cli.command('export-excel', help="Export to Excel")
@click.option('--filename', default='export.xlsx',
              help="name of the excel file")
@click.option('--outdir', type=click.Path(exists=True), default='.',
              help="output directory")
def export_excel(filename, outdir):
    stdin = click.get_text_stream('stdin')
    workbook = Workbook()
    workbook.remove_sheet(workbook.active)
    try:
        while True:
            entity = read_object(stdin)
            if entity is None:
                break
            sheet = _get_sheet(entity.schema, workbook)
            _write_entity(sheet, entity)
    except BrokenPipeError:
        raise click.Abort()
    finally:
        path = os.path.join(outdir, filename)
        workbook.save(path)
