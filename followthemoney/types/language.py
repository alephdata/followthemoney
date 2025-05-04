from typing import Optional, TYPE_CHECKING
from babel.core import Locale
from rigour.langs import iso_639_alpha3

from followthemoney.types.common import EnumType, EnumValues
from followthemoney.util import defer as _, gettext
from followthemoney.util import get_env_list

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


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
    max_length = 16

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
        "khm",
        "cnr",
        "ben",
    ]
    LANGUAGES = get_env_list("FTM_LANGUAGES", LANGUAGES)
    LANGUAGES = [lang.lower().strip() for lang in LANGUAGES]

    def _locale_names(self, locale: Locale) -> EnumValues:
        names = {
            "ara": gettext("Arabic"),
            "nor": gettext("Norwegian"),
            "cnr": gettext("Montenegrin"),
        }
        for lang in self.LANGUAGES:
            if lang not in names:
                names[lang] = lang
        for code, label in locale.languages.items():
            code = iso_639_alpha3(code)
            if code in self.LANGUAGES and names[code] == code:
                names[code] = label
        return names

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        code = iso_639_alpha3(text)
        if code not in self.LANGUAGES:
            return None
        return code
