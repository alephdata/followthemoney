from rdflib import URIRef  # type: ignore
from ipaddress import ip_address
from typing import Optional

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _


class IpType(PropertyType):
    name: str = 'ip'
    group: str = 'ips'
    label: str = _('IP-Address')
    plural: str = _('IP-Addresses')
    matchable: bool = True

    def validate(self, ip: str, **kwargs) -> bool:  # type: ignore[override] # noqa
        """Check to see if this is a valid ip address."""
        try:
            ip_address(ip)
            return True
        except ValueError:
            return False

    def clean_text(self, text: str, **kwargs) -> Optional[str]:  # type: ignore[override] # noqa
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        try:
            return str(ip_address(text))
        except ValueError:
            return None

    def rdf(self, value: str) -> URIRef:
        return URIRef('ip:%s' % value)
