from __future__ import unicode_literals

from normality import stringify
from stdnum import iban as iban_validator

from followthemoney.types.common import PropertyType


class IbanType(PropertyType):

    def validate(self, iban, **kwargs):
        iban = stringify(iban)
        if iban is None:
            return False

        try:
            return iban_validator.is_valid(iban)
        except iban.error:  # not a valid iban
            return False

    def clean_text(self, text, **kwargs):
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        text = text.replace(" ", "")
        text = text.upper()
        return text
