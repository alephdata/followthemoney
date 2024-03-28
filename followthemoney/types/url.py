from typing import Optional, TYPE_CHECKING
from rigour.urls import clean_url, compare_urls

from followthemoney.types.common import PropertyType
from followthemoney.rdf import URIRef, Identifier
from followthemoney.util import dampen, defer as _

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


class UrlType(PropertyType):
    """A uniform resource locator (URL). This will perform some normalisation
    on the URL so that it's sure to be using valid encoding/quoting, and to
    make sure the URL has a schema (e.g. `http`, `https`, ...)."""

    SCHEMES = ("http", "https", "ftp", "mailto")
    DEFAULT_SCHEME = "http"

    name = "url"
    group = "urls"
    label = _("URL")
    plural = _("URLs")
    matchable = True
    pivot = True

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        """Perform intensive care on URLs to make sure they have a scheme
        and a host name. If no scheme is given HTTP is assumed."""
        return clean_url(text)

    def compare(self, left: str, right: str) -> float:
        return compare_urls(left, right)

    def _specificity(self, value: str) -> float:
        return dampen(10, 120, value)

    def rdf(self, value: str) -> Identifier:
        return URIRef(value)

    def node_id(self, value: str) -> Optional[str]:
        return f"url:{value}"
