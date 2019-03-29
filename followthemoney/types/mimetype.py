from rdflib import URIRef
from pantomime import normalize_mimetype, DEFAULT

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class MimeType(PropertyType):
    name = 'mimetype'
    group = 'mimetypes'
    label = _('MIME-Type')
    plural = _('MIME-Types')
    matchable = False

    def clean_text(self, text, **kwargs):
        text = normalize_mimetype(text)
        if text != DEFAULT:
            return text

    def rdf(self, value):
        return URIRef('urn:mimetype:%s' % value)
