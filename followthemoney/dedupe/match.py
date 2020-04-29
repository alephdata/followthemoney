import json
from banal import is_mapping

from followthemoney.compare import compare
from followthemoney.util import get_entity_id


class Match(object):
    SAME = True
    DIFFERENT = False
    UNDECIDED = None

    def __init__(self, model, data):
        self.model = model
        self._data = data
        # Support output from Aleph's linkage API (profile_id):
        self.id = data.get('canonical_id', data.get('profile_id'))
        self.id = self.id or get_entity_id(data.get('canonical'))
        self._canonical = None
        self.entity_id = data.get('entity_id')
        self.entity_id = self.entity_id or get_entity_id(data.get('entity'))
        self._entity = None
        self.decision = data.get('decision')
        self._score = data.get('score', None)

    @property
    def entity(self):
        if self._entity is None:
            data = self._data.get('entity')
            if is_mapping(data) and 'schema' in data:
                self._entity = self.model.get_proxy(data)
        return self._entity

    @entity.setter
    def entity(self, entity):
        self._entity = entity
        self.entity_id = get_entity_id(entity)

    @property
    def canonical(self):
        if self._canonical is None:
            data = self._data.get('canonical')
            if is_mapping(data) and 'schema' in data:
                self._canonical = self.model.get_proxy(data)
        return self._canonical

    @canonical.setter
    def canonical(self, entity):
        self._canonical = entity
        self.id = get_entity_id(entity)

    def to_dict(self):
        data = {
            'canonical_id': self.id,
            'entity_id': self.entity_id,
        }
        if self.decision is not None:
            data['decision'] = self.decision
        if self._score is not None:
            data['score'] = self.score
        if self.entity is not None:
            data['entity'] = self.entity.to_dict()
        if self.canonical is not None:
            data['canonical'] = self.canonical.to_dict()
        return data

    @property
    def score(self):
        if self._score is not None:
            return self._score
        if self.entity and self.canonical:
            self._score = compare(self.model, self.entity, self.canonical)
            return self._score

    @classmethod
    def from_file(cls, model, fh):
        while True:
            line = fh.readline()
            if not line:
                break
            data = json.loads(line)
            yield cls(model, data)

    def __repr__(self):
        return '<Match(%r, %r, %s)>' % (self.id, self.entity_id, self.decision)
