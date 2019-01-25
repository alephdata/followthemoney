from rdflib import URIRef
from pantomime import normalize_mimetype, DEFAULT

from followthemoney.types.common import PropertyType


class MimeType(PropertyType):
    name = 'mimetype'
    group = 'mimetypes'
    matchable = False

    def clean_text(self, text, **kwargs):
        text = normalize_mimetype(text)
        if text != DEFAULT:
            return text

    def rdf(self, value):
        return URIRef('urn:mimetype:%s' % value)
