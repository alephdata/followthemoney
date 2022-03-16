from babel.core import Locale  # type: ignore

from followthemoney.types.common import EnumType, EnumValues
from followthemoney.rdf import URIRef, Identifier
from followthemoney.util import gettext, defer as _


class TopicType(EnumType):
    """Topics define a controlled vocabulary of terms applicable to some
    entities, such as companies and people. They describe categories of
    journalistic interest which may apply to the given entity, for example
    if a given person is a criminal or a politician.

    Besides the informative value, topics are ultimately supposed to bear
    fruits in the context of graph-based data analysis, where they would
    enable queries such as `find all paths between a government procurement
    award and a politician`."""

    name = "topic"
    group = "topics"
    label = _("Topic")
    plural = _("Topics")
    matchable = False

    _TOPICS = {
        "crime": _("Crime"),
        "crime.fraud": _("Fraud"),
        "crime.cyber": _("Cybercrime"),
        "crime.fin": _("Financial crime"),
        "crime.theft": _("Theft"),
        "crime.war": _("War crimes"),
        "crime.boss": _("Criminal leadership"),
        "crime.terror": _("Terrorism"),
        "crime.traffick": _("Trafficking"),
        "crime.traffick.drug": _("Drug trafficking"),
        "crime.traffick.human": _("Human trafficking"),
        "corp.offshore": _("Offshore"),
        "corp.shell": _("Shell company"),
        "gov": _("Government"),
        "gov.national": _("National government"),
        "gov.state": _("State government"),
        "gov.muni": _("Municipal government"),
        "gov.soe": _("State-owned enterprise"),
        "gov.igo": _("Intergovernmental organization"),
        "fin": _("Financial services"),
        "fin.bank": _("Bank"),
        "fin.fund": _("Fund"),
        "fin.adivsor": _("Financial advisor"),
        "role.pep": _("Politician"),  # don't FATF-splain me, bro.
        "role.rca": _("Close Associate"),
        "role.judge": _("Judge"),
        "role.civil": _("Civil servant"),
        "role.diplo": _("Diplomat"),
        "role.lawyer": _("Lawyer"),
        "role.acct": _("Accountant"),
        "role.spy": _("Spy"),
        "role.oligarch": _("Oligarch"),
        "role.journo": _("Journalist"),
        "role.act": _("Activist"),
        "pol.party": _("Political party"),
        "pol.union": _("Union"),
        "rel": _("Religion"),
        "mil": _("Military"),
        "asset.frozen": _("Frozen asset"),
        "sanction": _("Sanctioned entity"),
        "debarment": _("Debarred entity"),
        "poi": _("Person of interest"),
    }

    def _locale_names(self, locale: Locale) -> EnumValues:
        return {k: gettext(v) for (k, v) in self._TOPICS.items()}

    def rdf(self, value: str) -> Identifier:
        return URIRef(f"ftm:topic:{value}")
