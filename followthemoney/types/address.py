import re
from normality import slugify
from normality.cleaning import collapse_spaces

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import dampen


class AddressType(PropertyType):
    LINE_BREAKS = re.compile(r"(\r\n|\n|<BR/>|<BR>|\t|ESQ\.,|ESQ,|;)")
    COMMATA = re.compile(r"(,\s?[,\.])")
    name = "address"
    group = "addresses"
    label = _("Address")
    plural = _("Addresses")
    matchable = True
    pivot = True

    def clean_text(self, address, **kwargs):
        """Basic clean-up."""
        address = self.LINE_BREAKS.sub(", ", address)
        address = self.COMMATA.sub(", ", address)
        address = collapse_spaces(address)
        if len(address):
            return address

    def _specificity(self, value: str) -> float:
        return dampen(10, 60, value)

    def node_id(self, value: str) -> str:
        return "addr:%s" % slugify(value)
