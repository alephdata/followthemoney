from rdflib import URIRef  # type: ignore
from pantomime import normalize_mimetype, parse_mimetype  # type: ignore
from pantomime import DEFAULT

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class MimeType(PropertyType):
    """A MIME media type are a specification of a content type on a network.
    Each MIME type is assinged by IANA and consists of two parts: the type
    and sub-type. Common examples are: ``text/plain``, ``application/json`` and
    ``application/pdf``.

    MIME type properties do not contain parameters as used in HTTP headers,
    like ``charset=UTF-8``."""

    name = "mimetype"
    group = "mimetypes"
    label = _("MIME-Type")
    plural = _("MIME-Types")
    matchable = False

    def clean_text(self, text, **kwargs):
        text = normalize_mimetype(text)
        if text != DEFAULT:
            return text

    def rdf(self, value: str) -> URIRef:
        return URIRef(f"urn:mimetype:{value}")

    def caption(self, value: str) -> str:
        return parse_mimetype(value).label
