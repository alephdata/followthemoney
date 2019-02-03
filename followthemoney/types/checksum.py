from rdflib import URIRef

from followthemoney.types.common import PropertyType


class ChecksumType(PropertyType):
    """Used for content hashes, usually SHA1 (I know, I know)."""
    name = 'checksum'
    group = 'checksums'
    matchable = True

    def rdf(self, value):
        return URIRef('hash:%s' % value)
