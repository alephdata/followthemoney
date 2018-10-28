from rdflib import URIRef
from normality import stringify
from ipaddress import ip_address

from followthemoney.types.common import PropertyType


class IpType(PropertyType):
    name = 'ip'
    group = 'ips'
    strong = False

    def validate(self, ip, **kwargs):
        """Check to see if this is a valid ip address."""
        try:
            ip_address(ip)
            return True
        except ValueError:
            return False

    def clean(self, text, **kwargs):
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        text = stringify(text)
        if text is not None:
            try:
                return str(ip_address(text))
            except ValueError:
                return None

    def specificity(self, value):
        return 1

    def rdf(self, value):
        return URIRef('ip:%s' % value)
