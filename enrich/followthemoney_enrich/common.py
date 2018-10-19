from followthemoney import model
from followthemoney_enrich.cache import Cache


class Result(object):

    def __init__(self, enricher):
        self.enricher = enricher
        self.entities = []
        self.principal = None

    def make_entity(self, schema):
        entity = model.make_entity(schema, key_prefix=self.enricher.key_prefix)
        self.entities.append(entity)
        return entity

    def add_entity(self, entity):
        self.entities.append(entity)


class Enricher(object):
    cache = Cache()

    def expand_entity(self, entity):
        """Get adjacent entities to an entity."""
        pass

    def enrich_entity(self, entity):
        """Find possible candidates for an entity."""
        return []
