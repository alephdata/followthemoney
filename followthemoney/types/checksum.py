from rdflib import URIRef  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class ChecksumType(PropertyType):
    """Used for content hashes, usually SHA1 (I know, I know)."""
    name: str = 'checksum'
    group: str = 'checksums'
    label: str = _('Checksum')
    plural: str = _('Checksums')
    matchable: bool = True

    def rdf(self, value: str) -> URIRef:
        return URIRef('hash:%s' % value)
