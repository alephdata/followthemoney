import os
import logging
import requests
from uuid import uuid4
from pprint import pprint  # noqa
from requests.exceptions import RequestException
from banal import is_mapping, ensure_dict, ensure_list, hash_data
from urllib.parse import urljoin

from followthemoney.exc import InvalidData
from followthemoney_enrich.enricher import Enricher
from followthemoney_enrich.util import make_url

log = logging.getLogger(__name__)


class AlephEnricher(Enricher):
    key_prefix = 'aleph'
    TYPE_CONSTRAINT = 'LegalEntity'

    def __init__(self):
        self.host = os.environ.get('ALEPH_HOST')
        self.host = os.environ.get('ENRICH_ALEPH_HOST', self.host)
        self.api_base = urljoin(self.host, '/api/2/')
        self.api_key = os.environ.get('ALEPH_API_KEY')
        self.api_key = os.environ.get('ENRICH_ALEPH_API_KEY', self.api_key)
        self.session = requests.Session()
        self.session.headers['X-Aleph-Session'] = str(uuid4())
        if self.api_key is not None:
            self.session.headers['Authorization'] = 'ApiKey %s' % self.api_key

    def get_api(self, url, params=None):
        url = make_url(url, params)
        data = self.cache.get(url)
        if data is None:
            try:
                res = self.session.get(url)
                if res.status_code != 200:
                    return {}
                data = res.json()
                self.cache.store(url, data)
            except RequestException:
                log.exception("Error calling Aleph API")
                return {}
        return data

    def post_match(self, url, proxy):
        data = proxy.to_dict()
        key = proxy.id or hash_data(data)
        key = hash_data((url, key))
        if self.cache.has(key):
            # log.info("Cached [%s]: %s", self.host, proxy)
            return self.cache.get(key)

        log.info("Enrich [%s]: %s", self.host, proxy)
        try:
            res = self.session.post(url, json=data)
        except RequestException:
            log.exception("Error calling Aleph matcher")
            return {}
        if res.status_code != 200:
            return {}
        data = res.json()
        self.cache.store(key, data)
        return data

    def convert_entity(self, result, data):
        data = ensure_dict(data)
        if 'properties' not in data or 'schema' not in data:
            return
        try:
            entity = result.make_entity(data.get('schema'))
        except InvalidData:
            log.error("Server model mismatch: %s" % data.get('schema'))
            return
        entity.id = data.get('id')
        links = ensure_dict(data.get('links'))
        entity.add('alephUrl', links.get('self'))
        properties = ensure_dict(data.get('properties'))
        for prop, values in properties.items():
            for value in ensure_list(values):
                if is_mapping(value):
                    child = self.convert_entity(result, value)
                    if child.id is None:
                        continue
                    value = child.id
                try:
                    entity.add(prop, value, cleaned=True)
                except InvalidData:
                    msg = "Server property mismatch (%s): %s"
                    log.warning(msg % (entity.schema.name, prop))
        result.add_entity(entity)
        return entity

    def enrich_entity(self, entity):
        if not entity.schema.matchable:
            return

        url = urljoin(self.api_base, 'match')
        for page in range(10):
            data = self.post_match(url, entity)
            for res in data.get('results', []):
                result = self.make_result(entity)
                proxy = self.convert_entity(result, res)
                result.set_candidate(proxy)
                if result.candidate is not None:
                    yield result

            url = data.get('next')
            if url is None:
                break

    def expand_entity(self, entity):
        result = super(AlephEnricher, self).expand_entity(entity)
        for url in entity.get('alephUrl', quiet=True):
            _, entity_id = url.rsplit('/', 1)
            data = self.get_api(url)
            self.convert_entity(result, data)
            search_api = urljoin(self.api_base, 'search')
            params = {'filter:entities': entity_id}
            entities = self.get_api(search_api, params=params)
            for data in ensure_list(entities.get('results')):
                self.convert_entity(result, data)
        return result


class OccrpEnricher(AlephEnricher):

    def __init__(self):
        super(OccrpEnricher, self).__init__()
        self.host = 'https://data.occrp.org'
        self.api_base = urljoin(self.host, '/api/2/')
