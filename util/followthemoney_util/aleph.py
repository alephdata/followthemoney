import click
from urllib.parse import urljoin
from alephclient.api import AlephAPI

from followthemoney import model
from followthemoney_util.cli import cli
from followthemoney_util.util import write_entity


@cli.command('load-aleph', help='Stream data from an aleph instance')
@click.option('-f', '--foreign-id', help='Collection foreign ID')
@click.option('--api-url', envvar='ALEPH_HOST', help='Aleph API address', required=True)  # noqa
@click.option('--api-key', envvar='ALEPH_API_KEY', help='Aleph API key', required=True)  # noqa
def load_aleph(foreign_id, api_url, api_key):
    api = AlephAPI(api_url, api_key)
    collection_id = None
    if foreign_id is not None:
        collection = api.get_collection_by_foreign_id(foreign_id)
        if collection is None:
            raise click.BadParameter("Cannot find collection: %s" % foreign_id)
        collection_id = collection.get('id')

    stdout = click.get_text_stream('stdout')
    entities = api.stream_entities(collection_id=collection_id,
                                   include=['schema', 'properties'])
    for data in entities:
        if 'properties' not in data:
            continue
        entity = model.get_proxy(data)
        api_url = urljoin(api.base_url, 'entities/%s' % entity.id)
        entity.add('alephUrl', api_url, quiet=True)
        write_entity(stdout, entity)
