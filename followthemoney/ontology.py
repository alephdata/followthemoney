import sys
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import OWL, DCTERMS, RDF, RDFS, XSD

from followthemoney import model
from followthemoney.property import Property
from followthemoney.schema import Schema
from followthemoney.types import registry
from followthemoney.util import PathLike

NS = Namespace("https://schema.followthemoney.tech/#")


class Ontology(object):
    def __init__(self) -> None:
        self.uri = URIRef(NS)
        self.graph = Graph(identifier=self.uri)
        self.graph.namespace_manager.bind("ftm", NS)
        self.graph.namespace_manager.bind("owl", OWL)
        self.graph.namespace_manager.bind("dct", DCTERMS)

        self.graph.add((self.uri, RDF.type, OWL.Ontology))
        self.graph.add((self.uri, RDFS.label, Literal("Follow The Money")))
        modified = datetime.now().strftime("%Y-%m-%dT%H:%I:%M")
        modified = Literal(modified, datatype=XSD.dateTime)
        self.graph.add((self.uri, DCTERMS.modified, modified))

        self.add_schemata()

    def add_schemata(self) -> None:
        for schema in sorted(model):
            self.add_class(schema)

    def add_class(self, schema: Schema) -> None:
        suri = NS[schema.name]
        self.graph.add((suri, RDF.type, RDFS.Class))
        self.graph.add((suri, RDFS.isDefinedBy, self.uri))
        for parent in schema.extends:
            self.graph.add((suri, RDFS.subClassOf, NS[parent.name]))

        self.graph.add((suri, RDFS.label, Literal(schema.label)))
        if schema.description is not None:
            description = Literal(schema.description)
            self.graph.add((suri, RDFS.comment, description))

        for _, prop in sorted(schema.properties.items()):
            self.add_property(prop)

    def add_property(self, prop: Property) -> None:
        puri = NS[prop.qname]
        self.graph.add((puri, RDF.type, RDF.Property))
        self.graph.add((puri, RDFS.isDefinedBy, self.uri))

        self.graph.add((puri, RDFS.label, Literal(prop.label)))
        if prop.description is not None:
            self.graph.add((puri, RDFS.comment, Literal(prop.description)))

        self.graph.add((puri, RDFS.domain, NS[prop.schema.name]))
        if prop.range is not None:
            range = model.get(prop.range)
            if range is not None:
                self.graph.add((puri, RDFS.range, NS[range.name]))
        if prop.reverse is not None:
            self.graph.add((puri, OWL.inverseOf, NS[prop.reverse.qname]))
        if prop.type == registry.date:
            self.graph.add((puri, RDFS.range, XSD.dateTime))

    def write_namespace_docs(self, path: PathLike) -> None:
        xml_fn = "%s/ftm.xml" % path
        with open(xml_fn, "w") as xml_file:
            xml_file.write(self.graph.serialize(format="xml"))


if __name__ == "__main__":
    path = sys.argv[1]
    ontology = Ontology()
    ontology.write_namespace_docs(path)
    print("Namespace docs written to %s" % path)
