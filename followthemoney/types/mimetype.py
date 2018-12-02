from rdflib import URIRef
from normality import stringify
from pantomime import normalize_mimetype, DEFAULT

from followthemoney.types.common import PropertyType


class MimeType(PropertyType):
    name = 'mimetype'
    group = 'mimetypes'

    def validate(self, text, **kwargs):
        text = stringify(text)
        if text is None:
            return False
        return normalize_mimetype(text) is not None

    def clean_text(self, text, **kwargs):
        text = normalize_mimetype(text)
        if text != DEFAULT:
            return text

    def rdf(self, value):
        return URIRef('urn:mimetype:%s' % value)
