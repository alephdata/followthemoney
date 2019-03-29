from rdflib import URIRef
from urlnormalizer import normalize_url, is_valid_url

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class UrlType(PropertyType):
    name = 'url'
    group = 'urls'
    label = _('URL')
    plural = _('URLs')
    matchable = True

    def validate(self, url, **kwargs):
        """Check if `url` is a valid URL."""
        return is_valid_url(url)

    def clean_text(self, url, **kwargs):
        """Perform intensive care on URLs, see `urlnormalizer`."""
        return normalize_url(url)

    def rdf(self, value):
        return URIRef(value)
