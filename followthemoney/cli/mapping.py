import click
from banal import keys_values

from followthemoney import model
from followthemoney.namespace import Namespace
from followthemoney.mapping.source import StreamSource
from followthemoney.cli.cli import cli
from followthemoney.cli.util import write_object, load_mapping_file


@cli.command('map', help="Execute a mapping file and emit objects")
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('-s', '--signature', default=None, help='HMAC signature key')  # noqa
@click.argument('mapping_yaml', type=click.Path(exists=True))
def run_mapping(outfile, signature, mapping_yaml):
    config = load_mapping_file(mapping_yaml)
    try:
        ns = Namespace(signature)
        for dataset, meta in config.items():
            for mapping in keys_values(meta, 'queries', 'query'):
                entities = model.map_entities(mapping, key_prefix=dataset)
                for entity in entities:
                    if signature is not None:
                        entity = ns.apply(entity)
                    write_object(outfile, entity)
    except BrokenPipeError:
        raise click.Abort()
    except Exception as exc:
        raise click.ClickException(str(exc))


@cli.command('map-csv', help="Map CSV data from stdin and emit objects")
@click.option('-i', '--infile', type=click.File('r'), default='-')  # noqa
@click.option('-o', '--outfile', type=click.File('w'), default='-')  # noqa
@click.option('-s', '--signature', default=None, help='HMAC signature key')  # noqa
@click.argument('mapping_yaml', type=click.Path(exists=True))
def stream_mapping(infile, outfile, signature, mapping_yaml):
    sources = []
    config = load_mapping_file(mapping_yaml)
    for dataset, meta in config.items():
        for data in keys_values(meta, 'queries', 'query'):
            query = model.make_mapping(data, key_prefix=dataset)
            source = StreamSource(query, data)
            sources.append(source)

    try:
        ns = Namespace(signature)
        for record in StreamSource.read_csv(infile):
            for source in sources:
                if source.check_filters(record):
                    entities = source.query.map(record)
                    for entity in entities.values():
                        if signature is not None:
                            entity = ns.apply(entity)
                        write_object(outfile, entity)
    except BrokenPipeError:
        raise click.Abort()
