from rdflib import URIRef
from urlnormalizer import normalize_url, is_valid_url

from followthemoney.types.common import PropertyType


class UrlType(PropertyType):
    name = 'url'
    group = 'urls'
    matchable = True

    def validate(self, url, **kwargs):
        """Check if `url` is a valid URL."""
        return is_valid_url(url)

    def clean_text(self, url, **kwargs):
        """Perform intensive care on URLs, see `urlnormalizer`."""
        try:
            return normalize_url(url)
        except UnicodeDecodeError:
            return None

    def rdf(self, value):
        return URIRef(value)
