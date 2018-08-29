from nose.tools import assert_raises
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
        assert 'Thing' in model.to_dict(), model.to_dict()

        with assert_raises(KeyError):
            model['Banana']

        assert model.get_qname('Thing:name') == thing.get('name')

        props = list(model.properties)
        assert len(props), props
        assert thing.get('name') in props, props

    def test_schema_basics(self):
        thing = model.schemata['Thing']
        assert 'Thing' in repr(thing), repr(thing)
        assert thing.abstract, thing
        assert thing.label == thing.name, thing
        assert thing.get('name'), thing.properties
        assert not thing.get('banana'), thing.properties
        assert not len(list(thing.extends)), list(thing.extends)
        assert 1 == len(list(thing.schemata)), list(thing.schemata)

        person = model['Person']
        assert 1 == len(list(person.extends)), list(person.extends)
        assert 'Thing' in person.names, person.names

        ownership = model['Ownership']
        owner = ownership.get('owner')
        assert owner.range == 'LegalEntity'
        assert owner.reverse is not None
        role = ownership.get('role')
        assert role.reverse is None

    def test_schema_validate(self):
        thing = model.schemata['Thing']
        data = {'name': ['Banana']}
        value = thing.validate(data)
        assert value['name'] == data['name'], value

        with self.assertRaises(InvalidData):
            thing.validate({'name': None})

    def test_schema_invert(self):
        thing = model.schemata['Thing']
        data = {
            'schema': thing.name,
            'properties': {
                'name': ['Foo'],
                'alias': ['Foobar'],
                'country': ['de']
            }
        }
        out = thing.invert(data)
        # assert out['name'] == 'Foo', out
        assert 'Foo' in out['names'], out
        assert 'Foobar' in out['names'], out
        assert 'de' in out['countries'], out

    def test_model_precise_schema(self):
        assert model.precise_schema('Thing', 'Thing') == 'Thing'
        assert model.precise_schema('Thing', 'Person') == 'Person'
        assert model.precise_schema('Person', 'Thing') == 'Person'
        assert model.precise_schema('Person', 'Company') == 'LegalEntity'

        with assert_raises(InvalidData):
            model.precise_schema('Person', 'Directorship')

    def test_model_is_descendant(self):
        assert model['Thing'].is_a('Thing') is True
        assert model['LegalEntity'].is_a('Thing') is True
        assert model['Vessel'].is_a('Thing') is True
        assert model['Interest'].is_a('Interval') is True
        assert model['Ownership'].is_a('Interval') is True
        assert model['Ownership'].is_a('Interest') is True
        assert model['Payment'].is_a('Person') is False
        assert model['LegalEntity'].is_a('Vessel') is False
        assert model['Vessel'].is_a('LegalEntity') is False
        assert model['Ownership'].is_a('LegalEntity') is False

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
        assert name.required, name.required

        value, errors = name.validate('huhu')
        assert not errors, errors

        value, errors = name.validate(None)
        assert errors, errors
        assert not len(value), value

        person = model.get('Person')
        assert str(person.uri) == 'http://xmlns.com/foaf/0.1/Person'

    def test_descendants(self):
        le = model.schemata['LegalEntity']
        company = model.schemata['Company']
        descendants = list(le.descendants)
        assert company in descendants, descendants
        assert le not in descendants, descendants

    def test_model_reverse_properties(self):
        thing = model.schemata['Thing']
        sameAs = thing.get('sameAs')
        assert sameAs.reverse == sameAs, sameAs
        assert sameAs.stub is False, sameAs

        person = model.schemata['Person']
        assoc = model.schemata['Associate']
        prop = assoc.get('associate')
        assert prop.stub is False, prop
        assert prop.range == person, prop
        assert prop.reverse is not None
        rev = prop.reverse
        assert rev.range == assoc, rev
        assert rev.stub is True, rev
        assert rev.reverse == prop, rev

    def test_matchable(self):
        le = model.schemata['LegalEntity']
        company = model.schemata['Company']
        doc = model.schemata['Document']
        assert len(list(doc.matchable_schemata)) == 0
        matchable = list(company.matchable_schemata)
        assert company in matchable, matchable
        assert le in matchable, matchable
        assert doc not in matchable, matchable

    def test_model_featured_properties(self):
        interval = model.schemata['Interval']
        interest = model.schemata['Interest']
        assert 'startDate' in interval.featured and 'endDate' in \
            interval.featured, interval
        assert 'startDate' in interest.featured and 'endDate' in \
            interest.featured and 'role' in interest.featured, interest
