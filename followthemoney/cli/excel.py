import click

from followthemoney.cli.cli import cli
from followthemoney.cli.util import read_entity
from followthemoney.export.excel import get_workbook, write_entity


@cli.command('export-excel', help="Export to Excel")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.Path(), required=True)  # noqa
def export_excel(infile, outfile):
    workbook = get_workbook()
    try:
        while True:
            entity = read_entity(infile)
            if entity is None:
                break
            write_entity(workbook, entity)
        workbook.save(outfile)
    except BrokenPipeError:
        raise click.Abort()
