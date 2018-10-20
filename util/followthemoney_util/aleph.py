import json
import click
from urllib.parse import urljoin
from alephclient.api import AlephAPI

from followthemoney import model
from followthemoney_util.cli import cli


def get_collection_id(api, foreign_id, create=False):
    filters = [('foreign_id', foreign_id)]
    for coll in api.filter_collections(filters=filters, limit=1):
        if coll.get('foreign_id') == foreign_id:
            return coll.get('id')

    if create:
        coll = api.create_collection({
            'label': foreign_id,
            'casefile': False,
            'foreign_id': foreign_id
        })
        return coll.get('id')


@cli.command('load-aleph', help='Stream data from an aleph instance')
@click.option('-f', '--foreign-id', help='Collection foreign ID')
@click.option('--api-url', envvar='ALEPH_HOST', help='Aleph API address', required=True)  # noqa
@click.option('--api-key', envvar='ALEPH_API_KEY', help='Aleph API key', required=True)  # noqa
def load_aleph(foreign_id, api_url, api_key):
    api = AlephAPI(api_url, api_key)
    url = urljoin(api.base_url, 'entities/_stream')
    if foreign_id is not None:
        collection_id = get_collection_id(api, foreign_id)
        if collection_id is None:
            raise click.BadParameter("Cannot find collection: %s" % foreign_id)
        url = urljoin(api.base_url, 'collections/%s/_stream' % collection_id)

    stdout = click.get_text_stream('stdout')
    params = {'include': ['schema', 'properties']}
    res = api.session.get(url, params=params, stream=True)
    for line in res.iter_lines():
        data = json.loads(line)
        if 'properties' not in data:
            continue
        entity = model.get_proxy(data)
        api_url = urljoin(api.base_url, 'entities/%s' % entity.id)
        entity.add('alephUrl', api_url, quiet=True)
        data = json.dumps(entity.to_dict())
        stdout.write(data + '\n')
