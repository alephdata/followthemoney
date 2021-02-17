import re
import logging
from rdflib import URIRef  # type: ignore
from normality.cleaning import strip_quotes

from followthemoney.types.common import PropertyType
from followthemoney.types.domain import DomainType
from followthemoney.util import sanitize_text, defer as _

log = logging.getLogger(__name__)


class EmailType(PropertyType):
    """Internet mail address (e.g. user@example.com). These are notoriously hard
    to validate, but we use an irresponsibly simple rule and hope for the best."""

    REGEX_RAW = r"^[^@\s]+@[^@\s]+\.\w+$"
    REGEX = re.compile(REGEX_RAW)
    domains = DomainType()
    name = "email"
    group = "emails"
    label = _("E-Mail Address")
    plural = _("E-Mail Addresses")
    matchable = True
    pivot = True

    def validate(self, email, **kwargs):
        """Check to see if this is a valid email address."""
        # TODO: adopt email.utils.parseaddr
        email = sanitize_text(email)
        if email is None:
            return False
        if not self.REGEX.match(email):
            return False
        _, domain = email.rsplit("@", 1)
        return self.domains.validate(domain, **kwargs)

    def clean_text(self, email, **kwargs):
        """Parse and normalize an email address.

        Returns None if this is not an email address.
        """
        email = strip_quotes(email)
        if not self.REGEX.match(email):
            return None
        mailbox, domain = email.rsplit("@", 1)
        domain = self.domains.clean(domain, **kwargs)
        if domain is not None and mailbox is not None:
            return "@".join((mailbox, domain))

    # def country_hint(self, value)
    # TODO: do we want to use TLDs as country evidence?

    def rdf(self, value):
        return URIRef("mailto:%s" % value.lower())
