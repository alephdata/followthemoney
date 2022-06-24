from copy import deepcopy
from unittest import TestCase

from followthemoney import model
from followthemoney.compare import compare, compare_names

ENTITY = {
    "id": "test",
    "schema": "Person",
    "properties": {
        "name": ["Ralph Tester"],
        "birthDate": ["1972-05-01"],
        "idNumber": ["9177171", "8e839023"],
        "topics": ["role.spy"],
    },
}


class CompareTestCase(TestCase):
    def test_compare_names(self):
        left = {"schema": "Person", "properties": {"name": ["mr frank banana"]}}  # noqa
        left = model.get_proxy(left)
        right = {
            "schema": "Person",
            "properties": {"name": ["mr frank bananoid"]},
        }  # noqa
        right = model.get_proxy(right)
        same_score = compare_names(left, left)
        assert same_score > 0.5, same_score
        lr_score = compare_names(left, right)
        assert lr_score > 0.1, lr_score
        assert lr_score < same_score, (lr_score, same_score)

    def test_compare_countries(self):
        left = model.get_proxy(
            {
                "schema": "Person",
                "properties": {"name": ["Frank Banana"], "nationality": ["ie"]},
            }
        )
        no_country = model.get_proxy(
            {"schema": "Person", "properties": {"name": ["Frank Banana"]}}
        )
        baseline = compare(model, left, no_country)
        self.assertGreater(compare(model, left, left), baseline)

    def test_compare_basic(self):
        entity = model.get_proxy(ENTITY)
        best_score = compare(model, entity, entity)
        assert best_score > 0.5, best_score
        comp = model.get_proxy({"schema": "RealEstate"})
        self.assertAlmostEqual(compare(model, entity, comp), 0)
        self.assertAlmostEqual(compare(model, comp, comp), 0)

        comp = model.get_proxy({"schema": "Person"})
        self.assertAlmostEqual(compare(model, entity, comp), 0)

        comp = model.get_proxy({"schema": "LegalEntity"})
        self.assertAlmostEqual(compare(model, entity, comp), 0)

    def test_compare_quality(self):
        entity = model.get_proxy(ENTITY)
        best_score = compare(model, entity, entity)
        reduced = deepcopy(ENTITY)
        reduced["properties"].pop("birthDate")
        reduced["properties"].pop("idNumber")
        reduced_proxy = model.get_proxy(reduced)
        self.assertLess(compare(model, entity, reduced_proxy), best_score)

        reduced = deepcopy(ENTITY)
        reduced["properties"]["name"] = ["Frank Banana"]
        reduced_proxy = model.get_proxy(reduced)
        self.assertLess(compare(model, entity, reduced_proxy), best_score)
