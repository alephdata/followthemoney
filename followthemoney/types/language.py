from rdflib import URIRef
from languagecodes import iso_639_alpha3

from followthemoney.types.common import EnumType
from followthemoney.util import defer as _
from followthemoney.util import get_env_list


class LanguageType(EnumType):
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
                 'cat', 'npi']
    LANGUAGES = get_env_list('FTM_LANGUAGES', LANGUAGES)
    LANGUAGES = [l.lower().strip() for l in LANGUAGES]

    def _locale_names(self, locale):
        names = {}
        for lang in self.LANGUAGES:
            names[lang] = lang
        for code, label in locale.languages.items():
            code = iso_639_alpha3(code)
            if code in self.LANGUAGES:
                names[code] = label
        return names

    def clean_text(self, text, **kwargs):
        code = iso_639_alpha3(text)
        if code in self.LANGUAGES:
            return code

    def rdf(self, value):
        return URIRef('iso-639:%s' % value)
