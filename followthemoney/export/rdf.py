import logging
from prefixdate import Precision
from rdflib import Graph, Namespace
from rdflib.term import Identifier, URIRef, Literal
from rdflib import RDF, SKOS, XSD
from typing import Generator, List, Optional, TextIO, Tuple

from followthemoney.export.common import Exporter
from followthemoney.types import registry
from followthemoney.proxy import EntityProxy

log = logging.getLogger(__name__)
Triple = Tuple[Identifier, Identifier, Identifier]
NS = Namespace("https://schema.followthemoney.tech/#")


class RDFExporter(Exporter):
    """Export the entity as RDF N-Triples."""

    TYPE_PREFIXES = {
        registry.checksum: "hash:",
        registry.country: "http://id.loc.gov/vocabulary/countries/",
        registry.email: "mailto:",
        registry.entity: "e:",
        registry.gender: "gender:",
        registry.ip: "ip:",
        registry.identifier: "id:",
        registry.language: "http://lexvo.org/id/iso639-3/",
        registry.mimetype: "urn:mimetype:",
        registry.phone: "tel:",
        registry.topic: "ftm:topic:",
    }

    def __init__(self, fh: TextIO, qualified: bool = True) -> None:
        super(RDFExporter, self).__init__()
        self.fh = fh
        self.qualified = qualified

    def entity_triples(self, proxy: EntityProxy) -> Generator[Triple, None, None]:
        if proxy.id is None or proxy.schema is None:
            return
        entity_prefix = self.TYPE_PREFIXES[registry.entity]
        uri = URIRef(f"{entity_prefix}{proxy.id}")
        yield (uri, RDF.type, NS[proxy.schema.name])
        if self.qualified:
            caption = proxy.caption
            if caption != proxy.schema.label:
                yield (uri, SKOS.prefLabel, Literal(caption))
        for prop, value in proxy.itervalues():
            if prop.type in self.TYPE_PREFIXES:
                prefix = self.TYPE_PREFIXES[prop.type]
                if prop.type == registry.identifier and prop.format is not None:
                    prefix = f"{prefix}{prop.format}:"
                obj: Identifier = URIRef(f"{prefix}{value}")
            elif prop.type == registry.date:
                if len(value) < Precision.HOUR.value:
                    obj = Literal(value, datatype=XSD.date)
                else:
                    obj = Literal(value, datatype=XSD.dateTime)
            elif prop.type == registry.url:
                obj = URIRef(value)
            else:
                obj = Literal(value)
            if self.qualified:
                yield (uri, NS[prop.qname], obj)
            else:
                yield (uri, URIRef(prop.name), obj)

    def write(self, proxy: EntityProxy, extra: Optional[List[str]] = None) -> None:
        graph = Graph()

        for triple in self.entity_triples(proxy):
            graph.add(triple)
        try:
            nt = graph.serialize(format="nt11").strip()
            self.fh.write(nt + "\n")
        except Exception:
            log.exception("Failed to serialize ntriples.")
