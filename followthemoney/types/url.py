import logging
from urlnormalizer import normalize_url, is_valid_url

from followthemoney.types.common import PropertyType

log = logging.getLogger(__name__)


class UrlType(PropertyType):

    def validate(self, url, **kwargs):
        """Check if `url` is a valid URL."""
        return is_valid_url(url)

    def clean_text(self, url, **kwargs):
        """Perform intensive care on URLs, see `urlnormalizer`."""
        try:
            return normalize_url(url)
        except UnicodeDecodeError:
            log.warning("Invalid URL: %r", url)
