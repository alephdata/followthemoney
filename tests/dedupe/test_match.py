from unittest import TestCase
from copy import deepcopy

from followthemoney import model
from followthemoney.dedupe import Match

SAMPLE = {
    'decision': True,
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


class MatchTestCase(TestCase):

    def test_match_basic(self):
        match = Match(model, deepcopy(SAMPLE))
        assert match.id == 'can', match
        assert match.id == match.canonical.id, match
        assert match.entity_id == 'ent', match
        assert match.entity_id == match.entity.id, match

        assert match._score is None, match
        assert match.score is not None, match

        sample2 = deepcopy(SAMPLE)
        canon = sample2.pop('canonical')
        sample2['profile_id'] = canon.get('id')
        match = Match(model, sample2)
        assert match.id == 'can', match
        assert match.canonical is None, match
        assert match.entity is not None, match
        canon['id'] = 'banana'
        match.canonical = model.get_proxy(canon)
        assert match.id == 'banana', match
        match.entity = model.get_proxy(canon)
        assert match.entity_id == 'banana', match
        assert 'banana' in repr(match), repr(match)

    def test_match_to_dict(self):
        match = Match(model, deepcopy(SAMPLE))
        data = match.to_dict()
        assert data['canonical_id'] == 'can', data
        assert data['entity_id'] == 'ent', data
        assert 'score' not in data, data

        assert match.score is not None, match
        data = match.to_dict()
        assert 'score' in data, data
