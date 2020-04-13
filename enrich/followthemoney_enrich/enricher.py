import logging
from pprint import pprint  # noqa

from followthemoney import model
from followthemoney.dedupe import Match
from followthemoney_enrich.cache import Cache

log = logging.getLogger(__name__)


class Enricher(object):
    cache = Cache()
    name = None

    def make_match(self, canonical, entity):
        match = Match(model, {})
        match.canonical = model.get_proxy(canonical)
        match.entity = model.get_proxy(entity)
        return match

    def expand_entity(self, entity):
        """Get adjacent entities to an entity."""
        return []

    def enrich_entity_raw(self, entity):
        if not entity.schema.matchable:
            return
        yield from self.enrich_entity(entity)

    def enrich_entity(self, entity):
        """Find possible candidates for an entity."""
        return []
