import os
import yaml
import responses
from unittest import TestCase
from followthemoney import model
from followthemoney.exc import InvalidMapping


class MappingTestCase(TestCase):
    def setUp(self):
        self.fixture_path = os.path.join(os.path.dirname(__file__), "fixtures")
        db_path = os.path.join(self.fixture_path, "kek.sqlite")
        os.environ["FTM_TEST_DATABASE_URI"] = "sqlite:///" + db_path
        mapping_path = os.path.join(self.fixture_path, "kek.yml")
        with open(mapping_path, "r") as fh:
            self.kek_mapping = yaml.safe_load(fh)

    def test_kek_map_single(self):
        mapping = model.make_mapping(self.kek_mapping)
        assert len(mapping.source) == 2904, len(mapping.source)
        assert len(mapping.entities) == 3, mapping.entities
        assert len(mapping.refs) == 7, mapping.refs
        record = {
            "comp.id": 4,
            "sub.id": "7.4",
            "comp.name": "Pets.com Ltd",
            "shares.share": "40%",
            "comp.url": "https://pets.com",
            "sub.name": "DogFood Sales Corp.",
            "comp.address": "10 Broadstreet, 20388 Washington, DC",
        }
        entities = mapping.map(record)
        assert len(entities) == 3, entities.keys()
        company = entities.get("company")
        assert company.id, company
        assert record["comp.name"] in company.get("name"), company

    def test_mappings_with_links(self):
        url = "file://" + os.path.join(self.fixture_path, "links.csv")
        mapping_director = {
            "csv_url": url,
            "entities": {
                "director": {
                    "schema": "Person",
                    "key": "id",
                    "properties": {"name": {"column": "name"}},
                },
                "company": {
                    "schema": "Company",
                    "key": "comp_id",
                    "properties": {"name": {"column": "comp_name"}},
                },
                "directorship": {
                    "schema": "Directorship",
                    "keys": ["comp_id", "id"],
                    "properties": {
                        "director": {"entity": "director"},
                        "organization": {"entity": "company"},
                        "role": {"column": "role"},
                    },
                },
            },
        }
        entities = list(model.map_entities(mapping_director))
        assert len(entities) == 3, len(entities)

    def test_mappings_with_links_slavery(self):
        url = "file://" + os.path.join(self.fixture_path, "links.csv")
        mapping_slavery = {
            "csv_url": url,
            "entities": {
                "owner": {
                    "schema": "LegalEntity",
                    "key": "le_id",
                    "properties": {"name": {"column": "le_name"}},
                },
                "person": {
                    "schema": "Person",
                    "key": "person_id",
                    "properties": {"name": {"column": "name"}},
                },
                "ownership": {
                    "schema": "Ownership",
                    "keys": ["person_id", "le_id"],
                    "properties": {
                        "owner": {"entity": "owner"},
                        "asset": {"entity": "person"},
                        "percentage": {"column": "percentage"},
                    },
                },
            },
        }

        with self.assertRaises(InvalidMapping):
            list(model.map_entities(mapping_slavery))

    def test_mapping_with_literal_keys(self):
        url = "file://" + os.path.join(self.fixture_path, "links.csv")
        mapping = {
            "csv_url": url,
            "entities": {
                "director": {
                    "schema": "Person",
                    "key": "id",
                    "key_literal": "person",
                    "properties": {"name": {"column": "name"}},
                },
                "company": {
                    "schema": "LegalEntity",
                    "key": "id",
                    "key_literal": "legalentity",
                    "properties": {"name": {"column": "comp_name"}},
                },
            },
        }
        entities = list(model.map_entities(mapping))
        assert len(entities) == 2, len(entities)
        assert entities[0].id != entities[1].id, entities

    def test_kek_sqlite(self):
        entities = list(model.map_entities(self.kek_mapping))
        assert len(entities) == 8712, len(entities)
        ids = set([e.id for e in entities])
        assert len(ids) == 5607, len(ids)

    def test_local_csv_load(self):
        url = "file://" + os.path.join(self.fixture_path, "experts.csv")
        mapping = {"csv_url": url}
        with self.assertRaises(InvalidMapping):
            list(model.map_entities(mapping))
        mapping["entities"] = {
            "expert": {
                "schema": "Person",
                "properties": {
                    "name": {"column": "name"},
                    "nationality": {"column": "nationality"},
                    "gender": {"column": "gender"},
                },
            }
        }

        with self.assertRaises(InvalidMapping):
            entities = list(model.map_entities(mapping))

        mapping["entities"]["expert"]["key"] = "name"
        entities = list(model.map_entities(mapping))
        assert len(entities) == 14, len(entities)

        mapping["filters"] = {"gender": "male"}
        entities = list(model.map_entities(mapping))
        assert len(entities) == 10, len(entities)

        mapping["filters_not"] = {"nationality": "Portugal"}
        entities = list(model.map_entities(mapping))
        assert len(entities) == 7, len(entities)

        mapping["filters_not"] = {"nationality": ["Portugal", "Spain"]}
        entities = list(model.map_entities(mapping))
        assert len(entities) == 5, len(entities)

    @responses.activate
    def test_http_csv_load(self):
        with open(os.path.join(self.fixture_path, "experts.csv"), "r") as fh:
            data = fh.read()
        url = "http://pets.com/experts.csv"
        responses.add(
            responses.GET, url, body=data, status=200, content_type="text/csv"
        )
        mapping = {
            "csv_url": url,
            "entities": {
                "expert": {
                    "schema": "Person",
                    "key": "name",
                    "properties": {
                        "name": {"column": "name"},
                        "nationality": {"column": "nationality"},
                        "gender": {"column": "gender"},
                    },
                }
            },
        }
        entities = list(model.map_entities(mapping))
        assert len(entities) == 14, len(entities)

    def test_mapping_join(self):
        url = "file://" + os.path.join(self.fixture_path, "links.csv")
        mapping = {
            "csv_url": url,
            "entities": {
                "director": {
                    "schema": "Person",
                    "key": "id",
                    "key_literal": "person",
                    "properties": {
                        "name": {"column": "name"},
                        "address": {
                            "join": ", ",
                            "columns": ["house_number", "town", "zip"],
                        },
                    },
                }
            },
        }

        entities = list(model.map_entities(mapping))
        assert len(entities) == 1, len(entities)
        entity = entities[0]
        assert entity.get("address") == ["64, The Desert, 01234"], entity.to_dict()

    def test_mapping_split(self):
        url = "file://" + os.path.join(self.fixture_path, "links.csv")
        mapping = {
            "csv_url": url,
            "entities": {
                "director": {
                    "schema": "Person",
                    "key": "id",
                    "key_literal": "person",
                    "properties": {
                        "name": {"column": "name"},
                        "notes": {"split": "; ", "column": "fave_colours"},
                    },
                }
            },
        }

        entities = list(model.map_entities(mapping))
        assert len(entities) == 1, len(entities)
        self.assertCountEqual(
            entities[0].get("notes"), ["brown", "black", "blue"]
        )  # noqa
