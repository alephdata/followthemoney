import sys
import json
from datetime import datetime
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import OWL, DCTERMS, RDF, RDFS, XSD

from followthemoney import model, types


class Ontology(object):

    def __init__(self, ns_uri):

        self.ns_uri = ns_uri
        self.uri = URIRef(ns_uri)
        self.ns = Namespace(ns_uri)

        self.graph = Graph(identifier=ns_uri)
        self.graph.namespace_manager.bind('ftm', self.ns)
        self.graph.namespace_manager.bind('owl', OWL)
        self.graph.namespace_manager.bind('dct', DCTERMS)

        self.graph.add((self.uri, RDF.type, OWL.Ontology))
        self.graph.add((self.uri, RDFS.label, Literal("Follow The Money")))
        self.graph.add((self.uri, RDFS.comment, Literal(
            "A vocabulary for investigative reporting, based on real life.")))
        self.graph.add((self.uri, DCTERMS.modified,
                        Literal(datetime.now().strftime('%Y-%m-%dT%H:%I:%M'), datatype=XSD.dateTime)))

        self.add_schemata()

    def uri_for(self, thing):
        url = self.uri + thing.name  # Not using urljoin for this because it loses fragments
        return URIRef(url)

    def property_range(self, prop):
        if prop.type == types.entities:
            return self.uri_for(model[prop.range])
        elif prop.type == types.dates:
            return XSD.dateTime
        return None

    def add_class(self, entity):
        entity_uri = self.uri_for(entity)
        self.graph.add((entity_uri, RDF.type, RDFS.Class))
        self.graph.add((entity_uri, RDFS.isDefinedBy, self.uri))
        for extends in entity.extends:
            self.graph.add((entity_uri, RDFS.subClassOf,
                            self.uri_for(model[extends])))

        self.graph.add((entity_uri, RDFS.label, Literal(entity.label)))
        if entity.description is not None:
            self.graph.add((entity_uri, RDFS.comment,
                            Literal(entity.description)))

    def add_property(self, entity, prop):
        prop_uri = self.uri_for(prop)
        self.graph.add((prop_uri, RDF.type, RDF.Property))
        self.graph.add((prop_uri, RDFS.isDefinedBy, self.uri))

        self.graph.add((prop_uri, RDFS.label, Literal(prop.label)))
        if prop.description is not None:
            self.graph.add((prop_uri, RDFS.comment, Literal(prop.description)))

        self.graph.add((prop_uri, RDFS.domain, self.uri_for(entity)))
        prop_range = self.property_range(prop)
        if prop_range is not None:
            self.graph.add((prop_uri, RDFS.range, prop_range))

    def add_schemata(self):
        for schema in model:
            self.add_class(schema)
            for prop in schema._own_properties:
                self.add_property(schema, prop)

    def serialize(self, format='n3'):
        return self.graph.serialize(format=format)

    def jsonld_context(self):
        context = {
            '@context': {
                'xsd': 'http://www.w3.org/2001/XMLSchema#',
                'ftm': self.ns_uri
            }
        }

        for s, p, o in self.graph.triples((None, None, None)):
            name = s.split(self.ns_uri)[1]
            if name != "":
                # id_types = ['entity', 'url', 'uri']
                # if model.property_types.get(name) in id_types:
                #     context['@context'][name] = {
                #         '@id': 'ftm:%s' % name,
                #         '@type': '@id'
                #     }
                # elif model.property_types.get(name) == 'date':
                #     context['@context'][name] = {
                #         '@id': 'ftm:%s' % name,
                #         '@type': 'xsd:dateTime'
                #     }
                # else:
                context['@context'][name] = 'ftm:%s' % name

        return context

    def write_namespace_docs(self, path):
        ttl_fn = '%s/ftm.ttl' % path
        with open(ttl_fn, 'w') as ttl_file:
            ttl = self.serialize()
            ttl_file.write(ttl.decode('utf-8'))

        xml_fn = '%s/ftm.xml' % path
        with open(xml_fn, 'w') as xml_file:
            xml = self.serialize('xml')
            xml_file.write(xml.decode('utf-8'))

        json_fn = '%s/ftm.jsonld' % path
        with open(json_fn, 'w') as json_file:
            json_file.write(json.dumps(
                self.jsonld_context(), indent=4, sort_keys=True))


if __name__ == '__main__':
    uri = sys.argv[1]
    path = sys.argv[2]
    o = Ontology(uri)
    o.write_namespace_docs(path)
    print("Namespace docs written to %s" % path)
