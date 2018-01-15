from urlparse import urljoin
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL

from followthemoney import model


class Ontology(object):

    def __init__(self, ns_uri):

        self.uri = URIRef(ns_uri)
        self.ns = Namespace(ns_uri)

        self.graph = Graph(identifier=ns_uri)
        self.graph.namespace_manager.bind('ftm', self.ns)
        self.graph.namespace_manager.bind('owl', OWL)

        self.graph.add((self.uri, RDF.type, OWL.Ontology))
        self.graph.add((self.uri, RDFS.label, Literal("Follow The Money")))
        self.graph.add((self.uri, RDFS.comment, Literal(
            "A vocabulary for investigative reporting, based on real life.")))

        self.add_schemata()

    def uri_for(self, thing):
        url = urljoin(self.uri, thing.name)
        return URIRef(url)

    def property_range(self, prop):
        prop_type = model.property_types[prop.name]
        if prop_type == 'entity':
            return self.uri_for(model[prop.range])
        return None

    def add_class(self, entity):
        entity_uri = self.uri_for(entity)
        self.graph.add((entity_uri, RDF.type, RDFS.Class))
        for extends in entity.extends:
            self.graph.add((entity_uri, RDFS.subClassOf,
                            self.uri_for(model[extends])))

        self.graph.add((entity_uri, RDFS.label, Literal(entity.label)))
        if entity.description is not None:
            self.graph.add((entity_uri, RDFS.comment, Literal(entity.description)))

    def add_property(self, entity, prop):
        prop_uri = self.uri_for(prop)
        self.graph.add((prop_uri, RDF.type, RDF.Property))

        self.graph.add((prop_uri, RDFS.label, Literal(prop.label)))
        if prop.description is not None:
            self.graph.add((prop_uri, RDFS.comment, Literal(prop.description)))

        self.graph.add((prop_uri, RDFS.domain, self.uri_for(entity)))
        prop_range = self.property_range(prop)
        if prop_range is not None:
            self.graph.add((prop_uri, RDFS.range, prop_range))

    def add_schemata(self):
        for schema in model.schemata:
            self.add_class(model.schemata[schema])
            for prop in model.schemata[schema]._own_properties:
                self.add_property(model.schemata[schema], prop)

    def serialize(self, format='n3'):
        return self.graph.serialize(format=format)
