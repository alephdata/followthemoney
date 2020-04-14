import logging
from pkg_resources import iter_entry_points

from followthemoney_enrich.aleph import AlephEnricher  # noqa
from followthemoney_enrich.opencorporates import OpenCorporatesEnricher  # noqa
from followthemoney_enrich.cache import Cache, RedisCache

log = logging.getLogger(__name__)


def get_enrichers():
    for ep in iter_entry_points('followthemoney.enrich'):
        clazz = ep.load()
        clazz.name = ep.name
        yield clazz


def get_enricher(name):
    for clazz in get_enrichers():
        if clazz.name == name:
            return clazz


def enricher_cache():
    cache = Cache()
    if RedisCache.URL is not None:
        cache = RedisCache()
    return cache
