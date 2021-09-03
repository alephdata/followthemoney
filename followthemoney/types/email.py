import re
import logging
from typing import Optional
from rdflib import URIRef  # type: ignore
from rdflib.term import Identifier  # type: ignore
from urllib.parse import urlparse
from normality.cleaning import strip_quotes

from followthemoney.types.common import PropertyType
from followthemoney.util import sanitize_text, defer as _

log = logging.getLogger(__name__)


class EmailType(PropertyType):
    """Internet mail address (e.g. user@example.com). These are notoriously hard
    to validate, but we use an irresponsibly simple rule and hope for the best."""

    REGEX_RAW = r"^[^@\s]+@[^@\s]+\.\w+$"
    REGEX = re.compile(REGEX_RAW)
    name = "email"
    group = "emails"
    label = _("E-Mail Address")
    plural = _("E-Mail Addresses")
    matchable = True
    pivot = True

    # def _check_exists(self, domain):
    #     """Actually try to resolve a domain name."""
    #     try:
    #         domain = domain.encode('idna').lower()
    #         socket.getaddrinfo(domain, None)
    #         return True
    #     except:
    #         return False

    def validate(self, email, **kwargs):
        """Check to see if this is a valid email address."""
        # TODO: adopt email.utils.parseaddr
        email = sanitize_text(email)
        if email is None:
            return False
        if not self.REGEX.match(email):
            return False
        _, domain = email.rsplit("@", 1)
        if len(domain) < 4 or "." not in domain:
            return False
        return True

    def clean_text(self, email: str, **kwargs) -> Optional[str]:
        """Parse and normalize an email address.

        Returns None if this is not an email address.
        """
        email = strip_quotes(email)
        if not self.REGEX.match(email):
            return None
        mailbox, domain = email.rsplit("@", 1)
        # TODO: https://pypi.python.org/pypi/publicsuffix/
        # handle URLs by extracting the domain name
        domain = urlparse(domain).hostname or domain
        domain = domain.lower()
        domain = domain.rstrip(".")
        # handle unicode
        domain = domain.encode("idna").decode("ascii")
        if domain is not None and mailbox is not None:
            return "@".join((mailbox, domain))

    # def country_hint(self, value)
    # TODO: do we want to use TLDs as country evidence?

    def rdf(self, value: str) -> Identifier:
        return URIRef("mailto:%s" % value.lower())
