from rdflib import URIRef
from stdnum import iban
from stdnum.exceptions import ValidationError

from followthemoney.types.common import PropertyType
from followthemoney.util import sanitize_text, defer as _


class IbanType(PropertyType):
    name = 'iban'
    group = 'ibans'
    label = _('IBAN')
    plural = _('IBANs')
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
        return URIRef('iban:%s' % value)

    def node_id(self, value):
        return str(self.rdf(value.upper()))

    def caption(self, value):
        return iban.format(value)
