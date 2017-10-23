from unittest import TestCase
from followthemoney import model
from followthemoney.exc import InvalidData


class ModelTestCase(TestCase):

    def test_model_path(self):
        assert model.path.endswith('/schema'), model.path

    def test_model_basics(self):
        assert model.schemata['Thing'], model.schemata
        thing = model.schemata['Thing']
        assert thing == model.get(thing)
        assert thing in list(model), list(model)
        assert 'Person' in model.to_dict(), model.to_dict()
        assert 'Thing' not in model.to_dict(), model.to_dict()

    def test_schema_basics(self):
        thing = model.schemata['Thing']
        assert 'Thing' in repr(thing), repr(thing)
        assert thing.hidden, thing
        assert thing.label == thing.name, thing
        assert thing.get('name'), thing.properties
        assert not thing.get('banana'), thing.properties
        assert not len(list(thing.extends)), list(thing.extends)
        assert 1 == len(list(thing.schemata)), list(thing.schemata)

        person = model.schemata['Person']
        assert 1 == len(list(person.extends)), list(person.extends)
        assert 'Thing' in person.names, person.names

    def test_schema_validate(self):
        thing = model.schemata['Thing']
        data = {'name': 'Banana'}
        value = thing.validate(data)
        assert value['name'] == data['name'], value

        with self.assertRaises(InvalidData):
            thing.validate({})

    def test_model_precise_schema(self):
        assert model.precise_schema('Thing', 'Thing') == 'Thing'
        assert model.precise_schema('Thing', 'Person') == 'Person'
        assert model.precise_schema('Person', 'Thing') == 'Person'
        assert model.precise_schema('Person', 'Company') == 'LegalEntity'

    def test_model_merge(self):
        merged = model.merge({'schema': 'Person'},
                             {'schema': 'Company'})
        assert merged['schema'] == 'LegalEntity'

        merged = model.merge({}, {'id': 'banana'})
        assert merged['id'] == 'banana'

    def test_model_to_dict(self):
        thing = model.schemata['Thing']
        data = thing.to_dict()
        assert data['label'] == thing.label, data
        assert len(data['properties']) == len(list(thing.properties)), data

    def test_model_property(self):
        thing = model.schemata['Thing']
        name = thing.get('name')
        assert name.name in repr(name), repr(name)

        assert not name.is_multiple, name.is_multiple
        assert name.is_label, name.is_label

        value, errors = name.validate('huhu')
        assert not errors, errors

        value, errors = name.validate(None)
        assert errors, errors
        assert value is None, value
