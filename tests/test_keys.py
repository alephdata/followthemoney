import os
import yaml
from hashlib import sha1
from unittest import TestCase
from followthemoney import model
from followthemoney.exc import InvalidMapping


class MappingKeysTestCase(TestCase):
    def setUp(self):
        self.fixture_path = os.path.join(os.path.dirname(__file__), "fixtures")

        db_path = os.path.join(self.fixture_path, "kek.sqlite")
        os.environ["FTM_TEST_DATABASE_URI"] = "sqlite:///" + db_path

        mapping_path = os.path.join(self.fixture_path, "kek.yml")
        with open(mapping_path, "r") as fh:
            self.kek_mapping = yaml.safe_load(fh)

    def test_key_generation(self):
        mapping = model.make_mapping(
            {
                "csv_url": "http://pets.com",
                "entities": {"test": {"schema": "Person", "key": "id"}},
            }
        )
        for ent in mapping.entities:
            seed = ent.seed.hexdigest()
            assert seed == sha1(b"").hexdigest(), seed

        entities = mapping.map({})
        assert len(entities) == 0, entities.keys()
        entities = mapping.map({"id": "foo"})
        assert len(entities) == 1, entities.keys()
        ent0 = entities.get("test")
        assert ent0.id == sha1(b"foo").hexdigest(), ent0

    def test_multiple_keys(self):
        mapping = model.make_mapping(
            {
                "csv_url": "http://pets.com",
                "entities": {"test": {"schema": "Person", "key": ["b", "a"]}},
            }
        )
        entities = mapping.map({"a": "aaa", "b": "bbb"})
        ent0 = entities.get("test")
        assert ent0.id == sha1(b"aaabbb").hexdigest(), ent0

        mapping = model.make_mapping(
            {
                "csv_url": "http://pets.com",
                "entities": {"test": {"schema": "Person", "key": ["a", "b"]}},
            }
        )
        entities = mapping.map({"a": "aaa", "b": "bbb"})
        ent0 = entities.get("test")
        assert ent0.id == sha1(b"aaabbb").hexdigest(), ent0

    def test_key_literal(self):
        mapping = model.make_mapping(
            {
                "csv_url": "http://pets.com",
                "entities": {
                    "test": {
                        "schema": "Person",
                        "key_literal": "test",
                        "key": ["a", "b"],
                    }
                },
            }
        )
        entities = mapping.map({})
        assert len(entities) == 0, entities.keys()
        entities = mapping.map({"a": "aaa", "b": "bbb"})
        ent0 = entities.get("test")
        assert ent0.id == sha1(b"testaaabbb").hexdigest(), ent0
        # assert False, sha1('test').hexdigest()

    def test_key_column(self):
        csv_url = os.path.join(self.fixture_path, "experts.csv")
        mapping = {
            "csv_url": "file://" + csv_url,
            "entities": {
                "expert": {
                    "schema": "Person",
                    "key": "id",
                    "id_column": "id",
                    "properties": {
                        "name": {"column": "name"},
                        "nationality": {"column": "nationality"},
                        "gender": {"column": "gender"},
                    },
                }
            },
        }

        # only use key/keys or key_column
        with self.assertRaises(InvalidMapping):
            list(model.map_entities(mapping))

        del mapping["entities"]["expert"]["key"]

        entities = list(model.map_entities(mapping))
        self.assertEqual(len(entities), 14)
        self.assertEqual(entities[0].id, "1")
        self.assertEqual(entities[-1].id, "42")

    def test_key_column_from_sql(self):
        mapping = self.kek_mapping
        del mapping["entities"]["company"]["keys"]
        mapping["entities"]["company"]["id_column"] = "comp.id"

        mapped = model.make_mapping(mapping)
        assert len(mapped.source) == 2904, len(mapped.source)
        assert len(mapped.entities) == 3, mapped.entities
        assert len(mapped.refs) == 7, mapped.refs
        entities = list(model.map_entities(mapping))
        self.assertGreaterEqual(int(entities[0].id), 3000)  # FIXME?
