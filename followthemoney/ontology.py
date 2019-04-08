import sys
from datetime import datetime
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import OWL, DCTERMS, RDF, RDFS, XSD

from followthemoney import model
from followthemoney.types import registry
from followthemoney.util import NS


class Ontology(object):

    def __init__(self):
        self.uri = URIRef(NS)
        self.graph = Graph(identifier=self.uri)
        self.graph.namespace_manager.bind('ftm', NS)
        self.graph.namespace_manager.bind('owl', OWL)
        self.graph.namespace_manager.bind('dct', DCTERMS)

        self.graph.add((self.uri, RDF.type, OWL.Ontology))
        self.graph.add((self.uri, RDFS.label, Literal("Follow The Money")))
        modified = datetime.now().strftime('%Y-%m-%dT%H:%I:%M')
        modified = Literal(modified, datatype=XSD.dateTime)
        self.graph.add((self.uri, DCTERMS.modified, modified))

        self.add_schemata()

    def add_schemata(self):
        for schema in model:
            self.add_class(schema)

    def add_class(self, schema):
        self.graph.add((schema.uri, RDF.type, RDFS.Class))
        self.graph.add((schema.uri, RDFS.isDefinedBy, self.uri))
        for parent in schema.extends:
            self.graph.add((schema.uri, RDFS.subClassOf, parent.uri))

        self.graph.add((schema.uri, RDFS.label, Literal(schema.label)))
        if schema.description is not None:
            description = Literal(schema.description)
            self.graph.add((schema.uri, RDFS.comment, description))

        for prop in schema.properties.values():
            self.add_property(prop)

    def add_property(self, prop):
        self.graph.add((prop.uri, RDF.type, RDF.Property))
        self.graph.add((prop.uri, RDFS.isDefinedBy, self.uri))

        self.graph.add((prop.uri, RDFS.label, Literal(prop.label)))
        if prop.description is not None:
            self.graph.add((prop.uri, RDFS.comment, Literal(prop.description)))

        self.graph.add((prop.uri, RDFS.domain, prop.schema.uri))
        if prop.range is not None:
            range_uri = model.get(prop.range).uri
            self.graph.add((prop.uri, RDFS.range, range_uri))
        if prop.reverse is not None:
            self.graph.add((prop.uri, OWL.inverseOf, prop.reverse.uri))
        if prop.type == registry.date:
            self.graph.add((prop.uri, RDFS.range, XSD.dateTime))

    def serialize(self, format='n3'):
        return self.graph.serialize(format=format)

    def write_namespace_docs(self, path):
        ttl_fn = '%s/ftm.ttl' % path
        with open(ttl_fn, 'wb') as ttl_file:
            ttl_file.write(self.serialize())

        xml_fn = '%s/ftm.xml' % path
        with open(xml_fn, 'wb') as xml_file:
            xml_file.write(self.serialize('xml'))


if __name__ == '__main__':
    path = sys.argv[1]
    ontology = Ontology()
    ontology.write_namespace_docs(path)
    print("Namespace docs written to %s" % path)
