import logging
from rdflib import Graph

from followthemoney.export.common import Exporter

log = logging.getLogger(__name__)


class RDFExporter(Exporter):

    def __init__(self, fh, qualified=True):
        super(RDFExporter, self).__init__()
        self.fh = fh
        self.qualified = qualified

    def write(self, proxy, **kwargs):
        graph = Graph()
        for triple in proxy.triples(qualified=self.qualified):
            graph.add(triple)
        try:
            nt = graph.serialize(format='nt').strip()
            self.fh.write(nt.decode('utf-8') + '\n')
        except Exception:
            log.exception("Failed to serialize ntriples.")
