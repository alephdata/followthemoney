from copy import deepcopy
from unittest import TestCase

from followthemoney.compare import compare, compare_fingerprints


ENTITY = {
    'id': 'test',
    'schema': 'Person',
    'properties': {
        'name': 'Ralph Tester',
        'birthDate': '1972-05-01',
        'idNumber': ['9177171', '8e839023'],
        'website': 'https://ralphtester.me',
        'phone': '+12025557612',
        'email': 'info@ralphtester.me',
        'passport': 'passportEntityId'
    }
}


class CompareTestCase(TestCase):

    def test_compare_fingerprints(self):
        left = {'fingerprints': ['mr frank banana']}
        right = {'fingerprints': ['mr frank bananoid']}
        same_score = compare_fingerprints(left, left)
        assert same_score > 0.5, same_score
        lr_score = compare_fingerprints(left, right)
        assert lr_score > 0.1, lr_score
        assert lr_score < same_score, (lr_score, same_score)

    def test_compare_basic(self):
        best_score = compare(ENTITY, ENTITY)
        assert best_score > 0.5, best_score
        comp = {'id': 'bla', 'schema': 'RealEstate'}
        assert compare(ENTITY, comp) == 0
        assert compare(comp, comp) == 0

        reduced = deepcopy(ENTITY)
        reduced['properties'].pop('birthDate')
        assert compare(ENTITY, reduced) < best_score
