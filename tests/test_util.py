from unittest import TestCase
from followthemoney.util import merge_data


class UtilTestCase(TestCase):

    def test_merge_value(self):
        old = {
            'foo': 'bar',
        }
        new = {
            'foo': 'quux',
        }
        result = merge_data(old, new)
        assert result['foo'] == 'quux', result

    def test_merge_different(self):
        old = {
            'foo': 'quux',
        }
        new = {
            'bar': 'quux',
        }
        result = merge_data(old, new)
        assert result['foo'] == 'quux', result
        assert result['bar'] == 'quux', result

    def test_merge_list(self):
        old = {
            'lst': ['a', 'b', 'c']
        }
        new = {
            'lst': ['c', 'd', 'e']
        }
        result = merge_data(old, new)
        assert 'a' in result['lst'], result
        assert 'c' in result['lst'], result
        assert 'e' in result['lst'], result

    def test_merge_objects(self):
        old = {
            'data': {
                'nested': True
            }
        }
        new = {
            'data': {
                'banana': 'hello'
            }
        }
        result = merge_data(old, new)
        assert result['data']['nested'], result
        assert result['data']['banana'], result
