from rdflib import URIRef  # type: ignore
from pantomime import normalize_mimetype, parse_mimetype  # type: ignore
from pantomime import DEFAULT  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class MimeType(PropertyType):
    name = "mimetype"
    group = "mimetypes"
    label = _("MIME-Type")
    plural = _("MIME-Types")
    matchable = False

    def clean_text(self, text, **kwargs):
        text = normalize_mimetype(text)
        if text != DEFAULT:
            return text

    def rdf(self, value):
        return URIRef("urn:mimetype:%s" % value)

    def caption(self, value):
        return parse_mimetype(value).label
