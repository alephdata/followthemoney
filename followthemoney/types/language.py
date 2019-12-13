from rdflib import URIRef
from languagecodes import iso_639_alpha3

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import sanitize_text, get_locale, get_env_list


class LanguageType(PropertyType):
    name = 'language'
    group = 'languages'
    label = _('Language')
    plural = _('Languages')
    matchable = False

    # Language whitelist
    LANGUAGES = ['eng', 'fra', 'deu', 'rus', 'spa', 'nld', 'ron', 'kat',
                 'ara', 'tur', 'ltz', 'ell', 'lit', 'ukr', 'zho', 'bel',
                 'bul', 'bos', 'jpn', 'ces', 'lav', 'por', 'pol', 'hye',
                 'hrv', 'hin', 'heb', 'uzb', 'mon', 'urd', 'sqi', 'kor',
                 'isl', 'ita', 'est', 'nor', 'fas', 'swa', 'slv', 'slk',
                 'aze', 'tgk', 'kaz', 'tuk', 'kir', 'hun', 'dan', 'afr',
                 'swe', 'srp', 'ind', 'kan', 'mkd', 'mlt', 'msa', 'fin',
                 'cat']
    LANGUAGES = get_env_list('FTM_LANGUAGES', LANGUAGES)
    LANGUAGES = [l.lower().strip() for l in LANGUAGES]

    def __init__(self, *args):
        self._names = {}

    @property
    def names(self):
        locale = get_locale()
        if locale not in self._names:
            self._names[locale] = {}
            for lang in self.LANGUAGES:
                self._names[locale][lang] = lang
            for code, label in locale.languages.items():
                code = iso_639_alpha3(code)
                if code in self.LANGUAGES:
                    self._names[locale][code] = label
        return self._names[locale]

    def validate(self, text, **kwargs):
        text = sanitize_text(text)
        if text is None:
            return False
        return text in self.LANGUAGES

    def clean_text(self, text, **kwargs):
        code = iso_639_alpha3(text)
        if code in self.LANGUAGES:
            return code

    def rdf(self, value):
        return URIRef('iso-639:%s' % value)

    def caption(self, value):
        return self.names.get(value, value)

    def to_dict(self):
        data = super(LanguageType, self).to_dict()
        data['values'] = self.names
        return data
