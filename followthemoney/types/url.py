from rdflib import URIRef  # type: ignore
from urlnormalizer import normalize_url, is_valid_url  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class UrlType(PropertyType):
    name: str = 'url'
    group: str = 'urls'
    label: str = _('URL')
    plural: str = _('URLs')
    matchable: bool = True
    pivot: bool = True

    def validate(self, url: str, **kwargs) -> bool:  # type: ignore[override] # noqa
        """Check if `url` is a valid URL."""
        return is_valid_url(url)

    def clean_text(self, url: str, **kwargs) -> str:  # type: ignore[override] # noqa
        """Perform intensive care on URLs, see `urlnormalizer`."""
        return normalize_url(url)

    def rdf(self, value: str) -> URIRef:
        return URIRef(value)

    def node_id(self, value: str) -> str:
        return 'url:%s' % value
