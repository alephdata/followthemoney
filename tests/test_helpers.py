from followthemoney import model
from followthemoney.helpers import combine_names, remove_checksums
from followthemoney.helpers import simplify_provenance
from followthemoney.helpers import entity_filename
from followthemoney.helpers import name_entity, check_person_cutoff
from followthemoney.helpers import remove_prefix_dates


def test_remove_checksums():
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


def test_simplify_provenance():
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


def test_entity_filename():
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


def test_name_entity():
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


def test_death_cutoff():
    entity = model.make_entity("Company")
    assert not check_person_cutoff(entity)

    entity = model.make_entity("Person")
    entity.add("birthDate", "1985")
    assert not check_person_cutoff(entity)

    entity = model.make_entity("Person")
    entity.add("birthDate", "1985")
    entity.add("deathDate", "2022")
    assert not check_person_cutoff(entity)

    entity = model.make_entity("Person")
    entity.add("birthDate", "1800")
    assert check_person_cutoff(entity)

    entity = model.make_entity("Person")
    entity.add("birthDate", "1985")
    entity.add("deathDate", "2008")
    assert not check_person_cutoff(entity)


def test_remove_prefix_dates():
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


def test_combine_names():
    proxy = model.get_proxy(
        {
            "id": "banana",
            "schema": "Person",
            "properties": {
                "firstName": ["Vladimir", "Wladimir"],
                "fatherName": ["Vladimirovitch"],
                "lastName": ["Putin"],
            },
        }
    )
    combine_names(proxy)
    assert "Vladimir Putin" in proxy.get("alias"), proxy.get("alias")
    assert "Vladimir Vladimirovitch Putin" in proxy.get("alias"), proxy.get("alias")
    proxy = model.get_proxy(
        {
            "id": "banana",
            "schema": "Person",
            "properties": {
                "name": ["Vladimir Putin"],
            },
        }
    )
    combine_names(proxy)
    proxy = model.get_proxy(
        {
            "id": "banana",
            "schema": "Person",
            "properties": {
                "lastName": ["Putin"],
            },
        }
    )
    combine_names(proxy)
    assert "Putin" in proxy.get("alias"), proxy.get("alias")
