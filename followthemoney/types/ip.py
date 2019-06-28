from rdflib import URIRef
from ipaddress import ip_address

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class IpType(PropertyType):
    name = 'ip'
    group = 'ips'
    label = _('IP-Address')
    plural = _('IP-Addresses')
    matchable = True

    def validate(self, ip, **kwargs):
        """Check to see if this is a valid ip address."""
        try:
            ip_address(ip)
            return True
        except ValueError:
            return False

    def clean_text(self, text, **kwargs):
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        try:
            return str(ip_address(text))
        except ValueError:
            return None

    def rdf(self, value):
        return URIRef('ip:%s' % value)
