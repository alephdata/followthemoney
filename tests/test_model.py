from pytest import raises
from followthemoney import model
from followthemoney.types import registry
from followthemoney.exc import InvalidData


def test_model_path():
    assert model.path.endswith("/schema"), model.path


def test_model_basics():
    assert model.schemata["Thing"], model.schemata
    thing = model.schemata["Thing"]
    assert thing == model.get(thing)
    assert thing in list(model), list(model)
    data = model.to_dict()
    assert "schemata" in data, data
    assert len(data["schemata"]) == len(model.schemata)
    assert "Thing" in data["schemata"]
    assert "types" in data, data
    assert len(data["types"]) == len(list(registry.types))
    assert "name" in data["types"]
    assert "entity" in data["types"]

    with raises(KeyError):
        model["Banana"]

    assert model.get_qname("Thing:name") == thing.get("name")

    props = list(model.properties)
    assert len(props), props
    assert thing.get("name") in props, props


def test_model_type_schemata():
    schema = model.get_type_schemata(registry.checksum)
    assert model.get("Document") in schema, schema
    assert model.get("CourtCase") not in schema, schema


def test_schema_basics():
    thing = model.schemata["Thing"]
    assert "Thing" in repr(thing), repr(thing)
    assert thing.abstract, thing
    assert thing.label == thing.name, thing
    assert thing.get("name"), thing.properties
    assert not thing.get("banana"), thing.properties
    assert not len(list(thing.extends)), list(thing.extends)
    assert 1 == len(list(thing.schemata)), list(thing.schemata)

    person = model["Person"]
    assert 1 == len(list(person.extends)), list(person.extends)
    assert "Thing" in person.names, person.names

    ownership = model["Ownership"]
    owner = ownership.get("owner")
    assert owner.range == model["LegalEntity"]
    assert owner.reverse is not None
    role = ownership.get("role")
    assert role.reverse is None


def test_schema_validate():
    thing = model.schemata["Thing"]
    data = {"properties": {"name": ["Banana"]}}
    thing.validate(data)

    with raises(InvalidData):
        thing.validate({"properties": {"name": None}})


def test_model_common_schema():
    assert model.common_schema("Thing", "Thing") == model["Thing"]
    assert model.common_schema("Thing", "Person") == model["Person"]
    assert model.common_schema("Person", "Thing") == model["Person"]
    assert model.common_schema("LegalEntity", "Company") == model["Company"]
    assert model.common_schema("Interval", "Ownership") == model["Ownership"]
    # This behaviour turned out the be a really bad idea:
    # assert model.common_schema("LegalEntity", "Asset") == "Company"

    with raises(InvalidData):
        model.common_schema("Person", "Directorship")
    with raises(InvalidData):
        model.common_schema("Person", "Company")
    with raises(InvalidData):
        model.common_schema("Membership", "Thing")


def test_model_is_descendant():
    assert model["Thing"].is_a("Thing")
    assert model["LegalEntity"].is_a("Thing")
    assert model["Vessel"].is_a("Thing")
    assert model["Interest"].is_a("Interval")
    assert model["Ownership"].is_a("Interval")
    assert model["Ownership"].is_a("Interest")
    assert not model["Payment"].is_a("Person")
    assert not model["LegalEntity"].is_a("Vessel")
    assert not model["Vessel"].is_a("LegalEntity")
    assert not model["Ownership"].is_a("LegalEntity")


def test_make_entity():
    ent = model.make_entity("Person")
    assert ent.id is None
    assert ent.schema.name == "Person"


def test_model_to_dict():
    thing = model.schemata["Thing"]
    data = thing.to_dict()
    assert data["label"] == thing.label, data
    assert len(data["properties"]) == len(list(thing.properties)), data


def test_model_property():
    thing = model.schemata["Thing"]
    name = thing.get("name")
    assert name.name in repr(name), repr(name)
    assert not name.hidden, name.hidden
    assert name.validate("huhu") is None

    person = model.get("Person")
    assert str(person.uri) == "http://xmlns.com/foaf/0.1/Person"


def test_descendants():
    le = model.schemata["LegalEntity"]
    company = model.schemata["Company"]
    descendants = list(le.descendants)
    assert company in descendants, descendants
    assert le not in descendants, descendants


def test_model_reverse_properties():
    thing = model.schemata["Thing"]
    notes = thing.get("noteEntities")
    assert notes.stub is True, notes

    person = model.schemata["Person"]
    assoc = model.schemata["Associate"]
    prop = assoc.get("associate")
    assert prop.stub is False, prop
    assert prop.range == person, prop
    assert prop.reverse is not None
    rev = prop.reverse
    assert rev.range == assoc, (rev.range, assoc)
    assert rev.stub is True, rev
    assert rev.reverse == prop, rev


def test_matchable():
    le = model.schemata["LegalEntity"]
    company = model.schemata["Company"]
    doc = model.schemata["Document"]
    assert len(list(doc.matchable_schemata)) == 0
    matchable = list(company.matchable_schemata)
    assert company in matchable, matchable
    assert le in matchable, matchable
    assert doc not in matchable, matchable
    assert le.can_match(company)
    assert not doc.can_match(le)


def test_specificity_name():
    company = model.schemata["Company"]
    name = company.get("name")
    assert 0 == name.specificity("AA")
    assert 0.4 <= name.specificity("Church of Jesus Christ of the Latter Day Saints")  # noqa


def test_specificity_date():
    company = model.schemata["Company"]
    date = company.get("incorporationDate")
    spec = date.specificity("2011-01-01")
    assert 0.5 <= spec, spec

    date = company.get("retrievedAt")
    spec = date.specificity("2011-01-01")
    assert 0.0 == spec, spec


def test_model_featured_properties():
    directorship = model.schemata["Directorship"]
    assert (
        "startDate" in directorship.featured and "endDate" in directorship.featured
    ), directorship

    sprops = list(directorship.sorted_properties)
    assert len(sprops) == len(directorship.properties), sprops


def test_schema_temporal_extent():
    interval = model.schemata["Ownership"]
    event = model.schemata["Event"]

    assert interval.temporal_start == ["startDate", "date"]
    assert interval.temporal_end == ["endDate"]
    assert interval.temporal_start_props == [
        interval.get("startDate"),
        interval.get("date"),
    ]

    assert interval.temporal_end_props == [
        interval.get("endDate"),
    ]

    assert event.temporal_start == ["startDate", "date"]
    assert event.temporal_end == ["endDate"]
    assert interval.temporal_start_props == [
        interval.get("startDate"),
        interval.get("date"),
    ]
    assert interval.temporal_end_props == [
        interval.get("endDate"),
    ]
