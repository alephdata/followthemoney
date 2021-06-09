from unittest import TestCase

from followthemoney import model
from followthemoney.helpers import remove_checksums
from followthemoney.helpers import simplify_provenance
from followthemoney.helpers import entity_filename
from followthemoney.helpers import name_entity
from followthemoney.helpers import remove_prefix_dates


class HelpersTestCase(TestCase):
    def test_remove_checksums(self):
        proxy = model.get_proxy(
            {
                "id": "banana",
                "schema": "Document",
                "properties": {"contentHash": ["banana"], "title": ["foo"]},
            }
        )
        proxy = remove_checksums(proxy)
        assert not proxy.has("contentHash")
        assert proxy.has("title")

    def test_simplify_provenance(self):
        proxy = model.get_proxy(
            {
                "id": "banana",
                "schema": "Document",
                "properties": {
                    "publishedAt": ["2016-01-01", "2018-02-03"],
                    "modifiedAt": ["2016-01-01"],
                },
            }
        )
        proxy = simplify_provenance(proxy)
        assert 1 == len(proxy.get("modifiedAt")), proxy.get("modifiedAt")
        assert 1 == len(proxy.get("publishedAt")), proxy.get("publishedAt")
        assert "2016-01-01" in proxy.get("publishedAt")

    def test_entity_filename(self):
        proxy = model.get_proxy(
            {
                "id": "banana",
                "schema": "Document",
            }
        )
        file_name = entity_filename(proxy)
        assert "banana" == file_name, file_name

        proxy = model.get_proxy(
            {
                "id": "banana",
                "schema": "Document",
                "properties": {
                    "extension": [".doc"],
                },
            }
        )
        file_name = entity_filename(proxy)
        assert "banana.doc" == file_name, file_name

        proxy = model.get_proxy(
            {
                "id": "banana",
                "schema": "Document",
                "properties": {
                    "mimeType": ["application/pdf"],
                },
            }
        )
        file_name = entity_filename(proxy)
        assert "banana.pdf" == file_name, file_name

        proxy = model.get_proxy(
            {
                "id": "banana",
                "schema": "Document",
                "properties": {
                    "fileName": ["bla.doc"],
                },
            }
        )
        file_name = entity_filename(proxy)
        assert "bla.doc" == file_name, file_name
        file_name = entity_filename(proxy, extension="pdf")
        assert "bla.pdf" == file_name, file_name

    def test_name_entity(self):
        proxy = model.get_proxy(
            {
                "id": "banana",
                "schema": "Person",
                "properties": {
                    "name": ["Carl", "Karl", "Carlo", "CARL"],
                },
            }
        )
        name_entity(proxy)
        name = proxy.get("name")
        assert 1 == len(name), name
        assert name[0] not in proxy.get("alias"), proxy.get("alias")

        proxy = model.get_proxy(
            {
                "id": "banana",
                "schema": "Person",
                "properties": {
                    "name": ["Carl"],
                },
            }
        )
        name_entity(proxy)
        assert ["Carl"] == proxy.get("name"), proxy.get("name")

    def test_remove_prefix_dates(self):
        proxy = model.get_proxy(
            {
                "id": "banana",
                "schema": "Person",
                "properties": {
                    "birthDate": ["2020-01-05", "2020-01", "2020-03", "2020"],
                },
            }
        )
        remove_prefix_dates(proxy)
        assert "2020" not in proxy.get("birthDate")
        assert "2020-01" not in proxy.get("birthDate")
        assert "2020-01-05" in proxy.get("birthDate")
        assert "2020-03" in proxy.get("birthDate")
