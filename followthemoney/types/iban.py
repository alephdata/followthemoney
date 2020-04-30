from rdflib import URIRef  # type: ignore
from stdnum import iban  # type: ignore
from stdnum.exceptions import ValidationError  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import sanitize_text, defer as _


class IbanType(PropertyType):
    name: str = 'iban'
    group: str = 'ibans'
    label: str = _('IBAN')
    plural: str = _('IBANs')
    matchable: bool = True
    pivot: bool = True

    def validate(self, text: str, **kwargs) -> bool:
        _text = sanitize_text(text)
        try:
            return iban.validate(_text)
        except ValidationError:
            return False

    def clean_text(self, text: str, **kwargs) -> str:
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        return text.replace(" ", "").upper()

    def country_hint(self, value: str) -> str:
        return value[:2].lower()

    def rdf(self, value: str) -> URIRef:
        return URIRef('iban:%s' % value)

    def node_id(self, value: str) -> str:
        return str(self.rdf(value.upper()))

    def caption(self, value: str) -> str:  # type: ignore[override] # noqa
        return iban.format(value)
