import re
from rdflib import URIRef
from normality import stringify
from normality.cleaning import strip_quotes

from followthemoney.types.common import PropertyType
from followthemoney.types.domain import DomainType
from followthemoney.util import defer as _


class EmailType(PropertyType):
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    domains = DomainType()
    name = 'email'
    group = 'emails'
    label = _('E-Mail Address')
    plural = _('E-Mail Addresses')
    matchable = True

    def validate(self, email, **kwargs):
        """Check to see if this is a valid email address."""
        email = stringify(email)
        if email is None:
            return
        if not self.EMAIL_REGEX.match(email):
            return False
        mailbox, domain = email.rsplit('@', 1)
        return self.domains.validate(domain, **kwargs)

    def clean_text(self, email, **kwargs):
        """Parse and normalize an email address.

        Returns None if this is not an email address.
        """
        if not self.EMAIL_REGEX.match(email):
            return None
        email = strip_quotes(email)
        mailbox, domain = email.rsplit('@', 1)
        domain = self.domains.clean(domain, **kwargs)
        if domain is not None and mailbox is not None:
            return '@'.join((mailbox, domain))

    def normalize(self, email, **kwargs):
        """Normalize for comparison."""
        emails = super(EmailType, self).normalize(email, **kwargs)
        return [e.lower() for e in emails]

    # def country_hint(self, value)
    # TODO: do we want to use TLDs as country evidence?

    def rdf(self, value):
        return URIRef('mailto:%s' % value)
