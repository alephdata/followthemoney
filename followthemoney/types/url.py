from rdflib import URIRef  # type: ignore
from urlnormalizer import normalize_url, is_valid_url  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import dampen, defer as _


class UrlType(PropertyType):
    """A uniform resource locator (URL). This will perform some normalisation
    on the URL so that it's sure to be using valid encoding/quoting, and to
    make sure the URL has a schema (e.g. 'http', 'https', ...)."""

    name = "url"
    group = "urls"
    label = _("URL")
    plural = _("URLs")
    matchable = True
    pivot = True

    def validate(self, url, **kwargs):
        """Check if `url` is a valid URL."""
        return is_valid_url(url)

    def clean_text(self, url, **kwargs):
        """Perform intensive care on URLs, see `urlnormalizer`."""
        return normalize_url(url, drop_fragments=False)

    def _specificity(self, value):
        return dampen(10, 120, value)

    def rdf(self, value):
        return URIRef(value)

    def node_id(self, value):
        return "url:%s" % value
