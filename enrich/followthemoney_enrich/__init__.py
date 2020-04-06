import logging
from os import environ
from redis import Redis
from pkg_resources import iter_entry_points

from followthemoney_enrich.aleph import AlephEnricher, OccrpEnricher
from followthemoney_enrich.opencorporates import OpenCorporatesEnricher
from followthemoney_enrich.orbis import OrbisEnricher
from followthemoney_enrich.cache import Cache, RedisCache

REDIS_URL = environ.get('ENRICH_CACHE_REDIS_URL')

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
    if REDIS_URL is not None:
        try:
            
            redis = Redis.from_url(REDIS_URL)
            cache = RedisCache(redis)
        except ImportError:
            log.error("Configured to cache to redis, but "
                      "'redis' Python module is not installed.")
    return cache


__all__ = [
    OpenCorporatesEnricher,
    AlephEnricher,
    OccrpEnricher,
    OrbisEnricher
]
