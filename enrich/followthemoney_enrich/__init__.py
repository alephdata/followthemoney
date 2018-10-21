from pkg_resources import iter_entry_points

from followthemoney_enrich.aleph import AlephEnricher
from followthemoney_enrich.opencorporates import OpenCorporatesEnricher
from followthemoney_enrich.orbis import OrbisEnricher


def get_enrichers():
    for ep in iter_entry_points('followthemoney_enrich'):
        yield (ep.name, ep.load())


def get_enricher(name):
    for (cand, clazz) in get_enrichers():
        if cand == name:
            return clazz


__all__ = [
    OpenCorporatesEnricher,
    AlephEnricher,
    OrbisEnricher
]
