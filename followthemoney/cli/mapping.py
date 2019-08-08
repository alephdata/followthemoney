import click
from banal import keys_values

from followthemoney import model
from followthemoney.mapping.source import StreamSource
from followthemoney.cli.cli import cli
from followthemoney.cli.util import write_object, load_mapping_file


@cli.command('map', help="Execute a mapping file and emit objects")
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.argument('mapping_yaml', type=click.Path(exists=True))
def run_mapping(outfile, mapping_yaml):
    config = load_mapping_file(mapping_yaml)
    try:
        for dataset, meta in config.items():
            for mapping in keys_values(meta, 'queries', 'query'):
                entities = model.map_entities(mapping, key_prefix=dataset)
                for entity in entities:
                    write_object(outfile, entity)
    except BrokenPipeError:
        raise click.Abort()
    except Exception as exc:
        raise click.ClickException(str(exc))


@cli.command('map-csv', help="Map CSV data from stdin and emit objects")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.argument('mapping_yaml', type=click.Path(exists=True))
def stream_mapping(infile, outfile, mapping_yaml):
    sources = []
    config = load_mapping_file(mapping_yaml)
    for dataset, meta in config.items():
        for data in keys_values(meta, 'queries', 'query'):
            query = model.make_mapping(data, key_prefix=dataset)
            source = StreamSource(query, data)
            sources.append(source)

    try:
        for record in StreamSource.read_csv(infile):
            for source in sources:
                if source.check_filters(record):
                    entities = source.query.map(record)
                    for entity in entities.values():
                        write_object(outfile, entity)
    except BrokenPipeError:
        raise click.Abort()
