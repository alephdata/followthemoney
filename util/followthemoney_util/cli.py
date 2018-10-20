import json
import click

from followthemoney import model
from followthemoney_util.util import load_config_file, dict_list


@click.group(help="Command-line utility for FollowTheMoney graph data")
def cli():
    pass


@cli.command(help="Execute a mapping file and emit objects")
@click.argument('mapping_yaml', type=click.Path(exists=True))
def map(mapping_yaml):
    config = load_config_file(mapping_yaml)
    stream = click.get_text_stream('stdout')
    for dataset, meta in config.items():
        for mapping in dict_list(meta, 'queries', 'query'):
            entities = model.map_entities(mapping, key_prefix=dataset)
            for entity in entities:
                data = json.dumps(entity.to_dict())
                stream.write(data + '\n')


@cli.command(help="Format a stream of entities to make it readable")
def pretty():
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    try:
        while True:
            line = stdin.readline()
            if not line:
                break
            data = json.loads(line)
            data = json.dumps(data, indent=2)
            stdout.write(data + '\n')
    except BrokenPipeError:
        pass
