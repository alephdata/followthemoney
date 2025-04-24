import os
from tempfile import mkstemp
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from followthemoney import model
from followthemoney.export.rdf import RDFExporter, NS


ENTITY = {
    "id": "person",
    "schema": "Person",
    "properties": {
        "name": ["Ralph Tester"],
        "birthDate": ["1972-05-01"],
        "nationality": ["us"],
        "idNumber": ["9177171", "8e839023"],
        "website": ["https://ralphtester.me"],
        "phone": ["+12025557612"],
        "email": ["info@ralphtester.me"],
    },
}


def test_rdf_export():
    _, temp_path = mkstemp(suffix=".rdf")
    fh = open(temp_path, "w+")
    entity = model.get_proxy(ENTITY)
    exporter = RDFExporter(fh)
    exporter.write(entity)
    exporter.finalize()
    fh.seek(0)

    graph = Graph()
    graph.parse(fh, format="nt")
    assert len(graph) == 10, len(graph)

    nodes = graph.all_nodes()
    assert URIRef("e:person") in nodes
    assert URIRef("mailto:info@ralphtester.me") in nodes
    assert URIRef("https://ralphtester.me") in nodes
    assert URIRef("http://id.loc.gov/vocabulary/countries/us") in nodes
    for _, _, v in graph.triples((URIRef("e:person"), NS["name"], None)):
        assert v == "Ralph Tester"
    for _, _, v in graph.triples((URIRef("e:person"), RDF.type, None)):
        assert v == NS[entity.schema.name]

    os.unlink(temp_path)
