from rdflib import URIRef
from normality import stringify

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import get_locale


class LanguageType(PropertyType):
    name = 'language'
    group = 'languages'
    label = _('Language')
    plural = _('Languages')
    matchable = False

    def __init__(self, *args):
        self._names = {}

    @property
    def names(self):
        locale = get_locale()
        if locale not in self._names:
            self._names[locale] = {}
            for code, label in locale.languages.items():
                self._names[locale][code.lower()] = label
        return self._names[locale]

    def validate(self, text, **kwargs):
        text = stringify(text)
        if text is None:
            return False
        return text.lower() in self.names

    def clean_text(self, text, **kwargs):
        code = text.lower().strip()
        if code in self.names:
            return code

    def rdf(self, value):
        return URIRef('iso-639:%s' % value)

    def to_dict(self):
        data = super(LanguageType, self).to_dict()
        data['values'] = self.names
        return data
