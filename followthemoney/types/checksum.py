from followthemoney.rdf import URIRef, Identifier
from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class ChecksumType(PropertyType):
    """Content hashes calculated using SHA1. Checksum references are used by
    document-typed entities in Aleph to refer to raw data in the archive
    (e.g. the document from which the entity is extracted).

    Unfortunately, this has some security implications: in order to avoid people
    getting access to documents for which they know the checksum, properties
    of this type are scrubbed when submitted via the normal API. Checksums can only
    be defined by uploading a document to be ingested."""

    name = "checksum"
    group = "checksums"
    label = _("Checksum")
    plural = _("Checksums")
    matchable = True
    pivot = True

    def rdf(self, value: str) -> Identifier:
        return URIRef(f"hash:{value}")
