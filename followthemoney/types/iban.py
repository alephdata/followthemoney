from typing import Optional, TYPE_CHECKING
from rigour.ids import IBAN

from followthemoney.types.common import PropertyType
from followthemoney.rdf import URIRef, Identifier
from followthemoney.util import sanitize_text, defer as _

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


class IbanType(PropertyType):
    """An international bank account number, as defined in ISO 13616. IBANs are
    managed by SWIFT used in the European SEPA payment system.

    A notable aspect of IBANs is that they share a country prefix and validation
    mechanism, but the specific length of an IBAN is dependent on the country
    code defined in the first two characters: `NO8330001234567` and
    `CY21002001950000357001234567` are both valid values."""

    name = "iban"
    group = "ibans"
    label = _("IBAN")
    plural = _("IBANs")
    matchable = True
    pivot = True

    def validate(self, value: str, fuzzy: bool = False, format: Optional[str] = None) -> bool:
        text = sanitize_text(value)
        if text is None:
            return False
        return IBAN.is_valid(text)

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        return IBAN.normalize(text)

    def country_hint(self, value: str) -> str:
        return value[:2].lower()

    def rdf(self, value: str) -> Identifier:
        return URIRef(self.node_id(value))

    def node_id(self, value: str) -> str:
        return f"iban:{value.upper()}"

    def caption(self, value: str) -> str:
        return IBAN.format(value)
