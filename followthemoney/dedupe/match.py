import json

from followthemoney.util import get_entity_id
from followthemoney.namespace import Namespace


class Match(object):
    SAME = True
    DIFFERENT = False
    UNSURE = None

    def __init__(self, canonical_id=None, entity_id=None,
                 decision=None, score=None, **kwargs):
        self.canonical_id = Namespace.strip(get_entity_id(canonical_id))
        self.entity_id = get_entity_id(entity_id)
        self.naive_id = Namespace.strip(self.entity_id)
        self.decision = decision
        self.score = score

    def to_dict(self):
        return {
            'canonical': self.canonical_id,
            'entity': self.entity_id,
            'decision': self.decision,
            'score': self.score
        }

    @classmethod
    def from_dict(cls, data):
        # Support output from Aleph's linkage API
        canonical_id = data.pop('canonical', data.pop('profile_id', None))
        canonical_id = data.pop('canonical_id', canonical_id)
        entity_id = data.pop('entity', data.pop('entity_id', None))
        decision = data.pop('decision', data.pop('judgement', None))
        return cls(canonical_id=canonical_id,
                   entity_id=entity_id,
                   decision=decision,
                   score=data.pop('score', None),
                   **data)

    @classmethod
    def from_file(cls, fh):
        while True:
            line = fh.readline()
            if not line:
                break
            yield cls.from_dict(json.loads(line))

    def __repr__(self):
        return '<Match(%r, %r, %s)>' % \
            (self.canonical_id, self.entity_id, self.decision)
