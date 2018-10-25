from banal import ensure_list

from followthemoney import model
from followthemoney.compare import compare


class Result(object):

    def __init__(self, enricher, subject):
        self.enricher = enricher
        self._entities = {}
        self._candidate = None
        self._subject = None
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
        self._candidate = entity.id

    def set_subject(self, entity):
        if entity is None or entity.id is None:
            return
        self.add_entity(entity)
        self._subject = entity.id

    @property
    def entities(self):
        return self._entities.values()

    @property
    def subject(self):
        return self._entities.get(self._subject)

    @property
    def candidate(self):
        return self._entities.get(self._candidate)

    @property
    def score(self):
        if self.subject is None or self.candidate is None:
            return 0.0
        if self.subject.id == self.candidate.id:
            return 1.0
        return compare(model, self.subject, self.candidate)

    def to_dict(self):
        return {
            'entities': [e.to_dict() for e in self.entities],
            'subject': self._subject,
            'candidate': self._candidate,
            'enricher': self.enricher.name
        }

    @classmethod
    def from_dict(cls, enricher, data):
        result = cls(enricher, None)
        entities = ensure_list(data.get('entities'))
        entities = [model.get_proxy(e) for e in entities]
        entities = {e.id: e for e in entities}
        result._entities = entities
        result._subject = data.get('subject')
        result._candidate = data.get('candidate')
        return result
