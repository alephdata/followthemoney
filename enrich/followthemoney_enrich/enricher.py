import logging
from pprint import pprint  # noqa

from followthemoney_enrich.cache import Cache
from followthemoney_enrich.result import Result

log = logging.getLogger(__name__)


class Enricher(object):
    cache = Cache()
    name = None

    def make_result(self, subject):
        return Result(self, subject)

    def expand_entity(self, entity):
        """Get adjacent entities to an entity."""
        return self.make_result(entity)

    def enrich_entity(self, entity):
        """Find possible candidates for an entity."""
        return []

    def close(self):
        pass
