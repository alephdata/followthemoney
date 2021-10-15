from typing import Optional, TYPE_CHECKING
from ipaddress import ip_address

from followthemoney.types.common import PropertyType
from followthemoney.rdf import URIRef, Identifier
from followthemoney.util import defer as _

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


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

    def validate(self, value: str) -> bool:
        """Check to see if this is a valid ip address."""
        try:
            ip_address(value)
            return True
        except ValueError:
            return False

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        try:
            return str(ip_address(text))
        except ValueError:
            return None

    def rdf(self, value: str) -> Identifier:
        return URIRef(f"ip:{value}")
