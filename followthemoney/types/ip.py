from rdflib import URIRef  # type: ignore
from ipaddress import ip_address  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class IpType(PropertyType):
    """Internet protocol addresses. This supports both addresses used
    by the protocol versions 4 (e.g. ``192.168.1.143``) and 6
    (e.g. ``0:0:0:0:0:ffff:c0a8:18f``)."""

    name = "ip"
    group = "ips"
    label = _("IP-Address")
    plural = _("IP-Addresses")
    matchable = True
    pivot = True

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
        return URIRef("ip:%s" % value)
