from rdflib import URIRef  # type: ignore
from rdflib.term import Identifier  # type: ignore
from languagecodes import iso_639_alpha3

from followthemoney.types.common import EnumType
from followthemoney.util import defer as _
from followthemoney.util import get_env_list


class LanguageType(EnumType):
    """A human written language. This list is arbitrarily limited for some
    weird upstream technical reasons, but we'll happily accept pull requests
    for additional languages once there is a specific need for them to be
    supported."""

    name = "language"
    group = "languages"
    label = _("Language")
    plural = _("Languages")
    matchable = False

    # Language whitelist
    LANGUAGES = [
        "eng",
        "fra",
        "deu",
        "rus",
        "spa",
        "nld",
        "ron",
        "kat",
        "ara",
        "tur",
        "ltz",
        "ell",
        "lit",
        "ukr",
        "zho",
        "bel",
        "bul",
        "bos",
        "jpn",
        "ces",
        "lav",
        "por",
        "pol",
        "hye",
        "hrv",
        "hin",
        "heb",
        "uzb",
        "mon",
        "urd",
        "sqi",
        "kor",
        "isl",
        "ita",
        "est",
        "nor",
        "fas",
        "swa",
        "slv",
        "slk",
        "aze",
        "tgk",
        "kaz",
        "tuk",
        "kir",
        "hun",
        "dan",
        "afr",
        "swe",
        "srp",
        "ind",
        "kan",
        "mkd",
        "mlt",
        "msa",
        "fin",
        "cat",
        "nep",
        "tgl",
        "fil",
        "mya",
    ]
    LANGUAGES = get_env_list("FTM_LANGUAGES", LANGUAGES)
    LANGUAGES = [lang.lower().strip() for lang in LANGUAGES]

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

    def rdf(self, value: str) -> Identifier:
        return URIRef(f"iso-639:{value}")
