import logging
from typing import List, Optional, TextIO
from rdflib import Graph

from followthemoney.export.common import Exporter
from followthemoney.proxy import E

log = logging.getLogger(__name__)


class RDFExporter(Exporter):
    def __init__(self, fh: TextIO, qualified: bool = True) -> None:
        super(RDFExporter, self).__init__()
        self.fh = fh
        self.qualified = qualified

    def write(self, proxy: E, extra: Optional[List[str]] = None) -> None:
        graph = Graph()

        for triple in proxy.triples(qualified=self.qualified):
            graph.add(triple)
        try:
            nt = graph.serialize(format="nt11").strip()
            self.fh.write(nt + "\n")
        except Exception:
            log.exception("Failed to serialize ntriples.")
