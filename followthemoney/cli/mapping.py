import click
from banal import keys_values

from followthemoney import model
from followthemoney.mapping.source import StreamSource
from followthemoney.cli.cli import cli
from followthemoney.cli.util import write_object, load_mapping_file


@cli.command('map', help="Execute a mapping file and emit objects")
@click.argument('mapping_yaml', type=click.Path(exists=True))
def run_mapping(mapping_yaml):
    config = load_mapping_file(mapping_yaml)
    stream = click.get_text_stream('stdout')
    try:
        for dataset, meta in config.items():
            for mapping in keys_values(meta, 'queries', 'query'):
                entities = model.map_entities(mapping, key_prefix=dataset)
                for entity in entities:
                    write_object(stream, entity)
    except BrokenPipeError:
        raise click.Abort()
    except Exception as exc:
        raise click.ClickException(str(exc))


@cli.command('map-csv', help="Map CSV data from stdin and emit objects")
@click.argument('mapping_yaml', type=click.Path(exists=True))
def stream_mapping(mapping_yaml):
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')

    sources = []
    config = load_mapping_file(mapping_yaml)
    for dataset, meta in config.items():
        for data in keys_values(meta, 'queries', 'query'):
            query = model.make_mapping(data, key_prefix=dataset)
            source = StreamSource(query, data)
            sources.append(source)

    try:
        for record in StreamSource.read_csv(stdin):
            for source in sources:
                if source.check_filters(record):
                    entities = source.query.map(record)
                    for entity in entities.values():
                        write_object(stdout, entity)
    except BrokenPipeError:
        raise click.Abort()
