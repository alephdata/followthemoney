import logging
from os import environ
from pkg_resources import iter_entry_points

from followthemoney_enrich.aleph import AlephEnricher, OccrpEnricher
from followthemoney_enrich.opencorporates import OpenCorporatesEnricher
from followthemoney_enrich.orbis import OrbisEnricher
from followthemoney_enrich.cache import Cache, RedisCache, DatasetTableCache

REDIS_URL = environ.get('ENRICH_CACHE_REDIS_URL')
DATABASE_URL = environ.get('ENRICH_CACHE_DATABASE_URL')
DATABASE_TABLE = environ.get('ENRICH_CACHE_DATABASE_TABLE', 'enrich_cache')

log = logging.getLogger(__name__)


def get_enrichers():
    for ep in iter_entry_points('followthemoney_enrich'):
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
            from redis import Redis
            redis = Redis.from_url(REDIS_URL)
            cache = RedisCache(redis)
        except ImportError:
            log.error("Configured to cache to redis, but "
                      "'redis' Python module is not installed.")
    elif DATABASE_URL is not None:
        try:
            import dataset
            db = dataset.connect(DATABASE_URL)
            cache = DatasetTableCache(db[DATABASE_TABLE])
        except ImportError:
            log.error("Configured to cache to SQL, but "
                      "'dataset' Python module is not installed.")
    return cache


__all__ = [
    OpenCorporatesEnricher,
    AlephEnricher,
    OccrpEnricher,
    OrbisEnricher
]
