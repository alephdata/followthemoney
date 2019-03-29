from rdflib import URIRef

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class ChecksumType(PropertyType):
    """Used for content hashes, usually SHA1 (I know, I know)."""
    name = 'checksum'
    group = 'checksums'
    label = _('Checksum')
    plural = _('Checksums')
    matchable = True

    def rdf(self, value):
        return URIRef('hash:%s' % value)
