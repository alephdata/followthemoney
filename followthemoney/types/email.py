import re
import logging
from typing import Optional, List
from rdflib import URIRef  # type: ignore
from normality.cleaning import strip_quotes  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.types.domain import DomainType
from followthemoney.util import sanitize_text, defer as _

log = logging.getLogger(__name__)


class EmailType(PropertyType):
    EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.\w+$")
    domains: DomainType = DomainType()
    name: str = 'email'
    group: str = 'emails'
    label: str = _('E-Mail Address')
    plural: str = _('E-Mail Addresses')
    matchable: bool = True
    pivot: bool = True

    def validate(self, email: str, **kwargs) -> bool:  # type: ignore[override] # noqa
        """Check to see if this is a valid email address."""
        # TODO: adopt email.utils.parseaddr
        _email = sanitize_text(email)
        if _email is None:
            return False
        if not self.EMAIL_REGEX.match(_email):
            return False
        _, domain = _email.rsplit('@', 1)
        return self.domains.validate(domain, **kwargs)

    def clean_text(self, email: str, **kwargs) -> Optional[str]:  # type: ignore[override] # noqa
        """Parse and normalize an email address.

        Returns None if this is not an email address.
        """
        email = strip_quotes(email)
        if not self.EMAIL_REGEX.match(email):
            return None
        mailbox, domain = email.rsplit('@', 1)
        _domain = self.domains.clean(domain, **kwargs)
        if _domain is not None and mailbox is not None:
            return '@'.join((mailbox, _domain))
        return None

    def normalize(self, email: str, **kwargs) -> List:  # type: ignore[override] # noqa
        """Normalize for comparison."""
        emails = super(EmailType, self).normalize(email, **kwargs)
        return [e.lower() for e in emails]

    # def country_hint(self, value)
    # TODO: do we want to use TLDs as country evidence?

    def rdf(self, value: str) -> URIRef:
        return URIRef('mailto:%s' % value.lower())
