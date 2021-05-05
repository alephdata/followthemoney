from rdflib import URIRef  # type: ignore
from urllib.parse import urlparse

from followthemoney.types.common import PropertyType
from followthemoney.util import dampen, defer as _


class UrlType(PropertyType):
    """A uniform resource locator (URL). This will perform some normalisation
    on the URL so that it's sure to be using valid encoding/quoting, and to
    make sure the URL has a schema (e.g. 'http', 'https', ...)."""

    SCHEMES = ("http", "https", "ftp", "mailto")
    DEFAULT_SCHEME = "http"

    name = "url"
    group = "urls"
    label = _("URL")
    plural = _("URLs")
    matchable = True
    pivot = True

    def clean_text(self, url, **kwargs):
        """Perform intensive care on URLs to make sure they have a scheme
        and a host name. If no scheme is given HTTP is assumed."""
        try:
            parsed = urlparse(url)
        except (TypeError, ValueError):
            return None
        if not len(parsed.netloc):
            if "." in parsed.path and not url.startswith("//"):
                # This is a pretty weird rule meant to catch things like
                # 'www.google.com', but it'll likely backfire in some
                # really creative ways.
                return self.clean_text(f"//{url}", **kwargs)
            return None
        if not len(parsed.scheme):
            parsed = parsed._replace(scheme=self.DEFAULT_SCHEME)
        else:
            parsed = parsed._replace(scheme=parsed.scheme.lower())
        if parsed.scheme not in self.SCHEMES:
            return None
        if not len(parsed.path):
            parsed = parsed._replace(path="/")
        return parsed.geturl()

    def _specificity(self, value):
        return dampen(10, 120, value)

    def rdf(self, value):
        return URIRef(value)

    def node_id(self, value):
        return "url:%s" % value
