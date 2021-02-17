from rdflib import URIRef  # type: ignore
from stdnum import iban  # type: ignore
from stdnum.exceptions import ValidationError  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import sanitize_text, defer as _


class IbanType(PropertyType):
    """An international bank account number, as defined in ISO 13616. IBANs are
    managed by SWIFT used in the European SEPA payment system.

    A noteable aspect of IBANs is that they share a country prefix and validation
    mechanism, but the specific length of an IBAN is dependent on the country
    code defined in the first two characters: ``NO8330001234567`` and
    ``CY21002001950000357001234567`` are both valid values."""

    name = "iban"
    group = "ibans"
    label = _("IBAN")
    plural = _("IBANs")
    matchable = True
    pivot = True

    def validate(self, text, **kwargs):
        text = sanitize_text(text)
        try:
            return iban.validate(text)
        except ValidationError:
            return False

    def clean_text(self, text, **kwargs):
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        return text.replace(" ", "").upper()

    def country_hint(self, value):
        return value[:2].lower()

    def rdf(self, value):
        return URIRef(self.node_id(value))

    def node_id(self, value):
        return f"iban:{value.upper()}"

    def caption(self, value):
        return iban.format(value)
