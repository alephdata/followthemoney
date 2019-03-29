# TODO: https://pypi.python.org/pypi/publicsuffix/
# import socket
from normality import stringify
from urllib.parse import urlparse

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class DomainType(PropertyType):
    name = 'domain'
    group = None
    label = _('Domain')
    plural = _('Domains')
    matchable = True

    # def _check_exists(self, domain):
    #     """Actually try to resolve a domain name."""
    #     try:
    #         domain = domain.encode('idna').lower()
    #         socket.getaddrinfo(domain, None)
    #         return True
    #     except:
    #         return False

    def validate(self, obj, **kwargs):
        """Check if a thing is a valid domain name."""
        text = stringify(obj)
        if text is None:
            return False
        if '.' not in text:
            return False
        if '@' in text or ':' in text:
            return False
        if len(text) < 4:
            return False
        return True

    def clean_text(self, domain, **kwargs):
        """Try to extract only the domain bit from the """
        try:
            # handle URLs by extracting the domain name
            domain = urlparse(domain).hostname or domain
            domain = domain.lower()
            # get rid of port specs
            domain = domain.rsplit(':', 1)[0]
            domain = domain.rstrip('.')
            # handle unicode
            domain = domain.encode("idna").decode('ascii')
        except ValueError:
            return None
        if self.validate(domain):
            return domain
