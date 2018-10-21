from followthemoney import model
from followthemoney_enrich.cache import Cache


class Result(object):

    def __init__(self, enricher, subject):
        self.enricher = enricher
        self._entities = {}
        self.candidate = None
        self.subject = None
        self.set_subject(subject)

    def make_entity(self, schema):
        return model.make_entity(schema, key_prefix=self.enricher.key_prefix)

    def add_entity(self, entity):
        if entity is None or entity.id is None:
            return
        if entity.id in self._entities:
            self._entities[entity.id].merge(entity)
        else:
            self._entities[entity.id] = entity

    def set_candidate(self, entity):
        if entity is None or entity.id is None:
            return
        self.add_entity(entity)
        self.candidate = entity.id

    def set_subject(self, entity):
        if entity is None or entity.id is None:
            return
        self.add_entity(entity)
        self.subject = entity.id

    @property
    def entities(self):
        return self._entities.values()

    def to_dict(self):
        return {
            'entities': [e.to_dict() for e in self.entities],
            'subject': self.subject,
            'candidate': self.candidate
        }


class Enricher(object):
    cache = Cache()

    def make_result(self, subject):
        return Result(self, subject)

    def expand_entity(self, entity):
        """Get adjacent entities to an entity."""
        return self.make_result(entity)

    def enrich_entity(self, entity):
        """Find possible candidates for an entity."""
        return []
