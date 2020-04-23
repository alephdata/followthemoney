import logging
from pprint import pprint  # noqa
from alephclient.api import AlephAPI
from requests.exceptions import RequestException
from banal import is_mapping, ensure_dict, ensure_list, hash_data

from followthemoney import model
from followthemoney.exc import InvalidData
from followthemoney_enrich.enricher import Enricher

log = logging.getLogger(__name__)


class AlephEnricher(Enricher):

    def __init__(self):
        self.api = AlephAPI()

    def get_api(self, url):
        data = self.cache.get(url)
        if data is not None:
            return data
        try:
            log.info("Aleph fetch: %s", url)
            res = self.api.session.get(url)
            if res.status_code != 200:
                return {}
            data = res.json()
            self.cache.store(url, data)
            return data
        except RequestException:
            log.exception("Error calling Aleph API")
            return {}

    def post_match(self, url, proxy):
        data = proxy.to_dict()
        key = proxy.id or hash_data(data)
        key = hash_data((url, key))
        if self.cache.has(key):
            log.info("Cached [%s]: %s", key, url)
            return self.cache.get(key)

        log.info("Enrich: %r", proxy)
        try:
            res = self.api.session.post(url, json=data)
        except RequestException:
            log.exception("Error calling Aleph matcher")
            return {}
        if res.status_code != 200:
            return {}
        data = res.json()
        self.cache.store(key, data)
        return data

    def convert_entity(self, data):
        data = ensure_dict(data)
        if 'properties' not in data or 'schema' not in data:
            return
        try:
            entity = model.get_proxy(data, cleaned=False)
        except InvalidData:
            log.error("Server model mismatch: %s" % data.get('schema'))
            return
        entity.id = data.get('id')
        links = ensure_dict(data.get('links'))
        entity.add('alephUrl', links.get('self'),
                   quiet=True, cleaned=True)
        collection = data.get('collection', {})
        entity.add('publisher', collection.get('label'),
                   quiet=True, cleaned=True)
        clinks = collection.get('links', {})
        entity.add('publisherUrl', clinks.get('ui'),
                   quiet=True, cleaned=True)
        return entity

    def convert_nested(self, data):
        entity = self.convert_entity(data)
        properties = ensure_dict(data.get('properties'))
        for prop, values in properties.items():
            for value in ensure_list(values):
                if is_mapping(value):
                    yield self.convert_entity(value)
        yield entity

    def enrich_entity(self, entity):
        url = self.api._make_url('match')
        for page in range(10):
            data = self.post_match(url, entity)
            for res in data.get('results', []):
                proxy = self.convert_entity(res)
                yield self.make_match(entity, proxy)

            url = data.get('next')
            if url is None:
                break

    def expand_entity(self, entity):
        for url in entity.get('alephUrl', quiet=True):
            data = self.get_api(url)
            yield from self.convert_nested(data)

            _, entity_id = url.rsplit('/', 1)
            filters = (('entities', entity_id),)
            search_api = self.api._make_url('entities', filters=filters)
            while True:
                res = self.get_api(search_api)
                for data in ensure_list(res.get('results')):
                    yield from self.convert_nested(data)

                search_api = res.get('next')
                if search_api is None:
                    break
