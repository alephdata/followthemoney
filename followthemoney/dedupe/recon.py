import json
from followthemoney.util import get_entity_id
from followthemoney.namespace import Namespace


class Recon(object):
    MATCH = 't'
    DISTINCT = 'f'
    UNSURE = '?'

    __slots__ = ['subject', 'canonical', 'judgement']

    def __init__(self, subject, canonical, judgement):
        self.subject, _ = Namespace.parse(get_entity_id(subject))
        self.canonical, _ = Namespace.parse(get_entity_id(canonical))
        self.judgement = judgement or self.UNSURE

    def to_dict(self):
        return dict(subject=self.subject,
                    canonical=self.canonical,
                    judgement=self.judgement)

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        return cls(subject=data.get('subject'),
                   canonical=data.get('canonical'),
                   judgement=data.get('judgement'))

    @classmethod
    def from_json(cls, text):
        return cls.from_dict(json.loads(text))

    @classmethod
    def from_file(cls, fh):
        while True:
            line = fh.readline()
            if not line:
                break
            yield cls.from_json(line)
