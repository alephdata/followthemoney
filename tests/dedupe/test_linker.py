from unittest import TestCase
from copy import deepcopy

from followthemoney import model
from followthemoney.dedupe import Linker, Match

SAMPLE = {
    'decision': False,
    'canonical': {
        'id': 'can',
        'schema': 'Person',
        'properties': {
            'name': ['Tom']
        }
    },
    'entity': {
        'id': 'ent',
        'schema': 'LegalEntity',
        'properties': {
            'name': ['Thomas']
        }
    }
}


class LinkerTestCase(TestCase):

    def test_linker(self):
        match = Match(model, deepcopy(SAMPLE))
        match.decision = True
        passport = model.get_proxy({
            'id': 'pass',
            'schema': 'Passport',
            'properties': {
                'holder': ['ent']
            }
        })
        linker = Linker(model)
        linker.add(match)
        out = linker.apply(match.entity)
        assert out.id == 'can', out
        out = linker.apply(passport)
        assert 'can' in out.get('holder'), out
        assert 'ent' not in out.get('holder'), out

    def test_linker_noop(self):
        match = Match(model, deepcopy(SAMPLE))
        passport = model.get_proxy({
            'id': 'pass',
            'schema': 'Passport',
            'properties': {
                'holder': ['ent']
            }
        })
        linker = Linker(model)
        linker.add(match)
        out = linker.apply(match.entity)
        assert out.id == 'ent', out
        out = linker.apply(passport)
        assert 'ent' in out.get('holder'), out
        assert 'can' not in out.get('holder'), out
