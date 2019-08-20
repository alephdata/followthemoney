import click

from followthemoney.cli.cli import cli
from followthemoney.cli.util import export_stream
from followthemoney.export.csv import CSVExporter


@cli.command('export-csv', help="Export to CSV")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outdir', type=click.Path(file_okay=False, writable=True), default='.', help="output directory")  # noqa
def export_csv(infile, outdir):
    exporter = CSVExporter(outdir)
    export_stream(exporter, infile)
