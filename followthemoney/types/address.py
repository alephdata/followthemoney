from typing import Optional
import re
from normality import slugify  # type: ignore
from normality.cleaning import collapse_spaces  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import dampen


class AddressType(PropertyType):
    LINE_BREAKS = re.compile(r'(\r\n|\n|<BR/>|<BR>|\t|ESQ\.,|ESQ,|;)')
    COMMATA = re.compile(r'(,\s?[,\.])')
    name: str = 'address'
    group: str = 'addresses'
    label: str = _('Address')
    plural: str = _('Addresses')
    matchable: bool = True
    pivot: bool = True

    def clean_text(self, address: str, **kwargs) -> Optional[str]:  # type: ignore[override] # noqa
        """Basic clean-up."""
        address = self.LINE_BREAKS.sub(', ', address)
        address = self.COMMATA.sub(', ', address)
        address = collapse_spaces(address)
        if len(address):
            return address
        return None

    # TODO: normalize well-known parts like "Street", "Road", etc.
    # TODO: consider using https://github.com/openvenues/pypostal
    # def normalize(self, address, **kwargs):
    #     """Make the address more compareable."""
    #     addresses = super(AddressType, self).normalize(address, **kwargs)
    #     return addresses

    def _specificity(self, value: str) -> float:
        return dampen(10, 60, value)

    def node_id(self, value: str) -> str:
        return 'addr:%s' % slugify(value)
