from rdflib import URIRef  # type: ignore
from pantomime import normalize_mimetype, parse_mimetype, DEFAULT  # type: ignore
from typing import Optional

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class MimeType(PropertyType):
    name: str = 'mimetype'
    group: str = 'mimetypes'
    label: str = _('MIME-Type')
    plural: str = _('MIME-Types')
    matchable: bool = False

    def clean_text(self, text: str, **kwargs) -> Optional[str]:  # type: ignore[override] # noqa
        text = normalize_mimetype(text)
        if text != DEFAULT:
            return text
        return None

    def rdf(self, value: str) -> URIRef:
        return URIRef('urn:mimetype:%s' % value)

    def caption(self, value: str) -> str:  # type: ignore[override] # noqa
        return parse_mimetype(value).label
