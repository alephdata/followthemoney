from pkg_resources import iter_entry_points

from followthemoney_enrich.aleph import AlephEnricher, OccrpEnricher
from followthemoney_enrich.opencorporates import OpenCorporatesEnricher
from followthemoney_enrich.orbis import OrbisEnricher


def get_enrichers():
    for ep in iter_entry_points('followthemoney_enrich'):
        clazz = ep.load()
        clazz.name = ep.name
        yield clazz


def get_enricher(name):
    for clazz in get_enrichers():
        if clazz.name == name:
            return clazz


__all__ = [
    OpenCorporatesEnricher,
    AlephEnricher,
    OccrpEnricher,
    OrbisEnricher
]
