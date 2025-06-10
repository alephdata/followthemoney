from babel.core import Locale

from followthemoney.types.common import EnumType, EnumValues
from followthemoney.util import gettext, defer as _


class TopicType(EnumType):
    """Topics define a controlled vocabulary of terms applicable to some
    entities, such as companies and people. They describe categories of
    journalistic interest which may apply to the given entity, for example
    if a given person is a criminal or a politician.

    Besides the informative value, topics are ultimately supposed to bear
    fruits in the context of graph-based data analysis, where they would
    enable queries such as _find all paths between a government procurement
    award and a politician_."""

    name = "topic"
    group = "topics"
    label = _("Topic")
    plural = _("Topics")
    matchable = False
    max_length = 64

    _TOPICS = {
        "crime": _("Crime"),
        "crime.fraud": _("Fraud"),
        "crime.cyber": _("Cybercrime"),
        "crime.fin": _("Financial crime"),
        "crime.env": _("Environmental violations"),
        "crime.theft": _("Theft"),
        "crime.war": _("War crimes"),
        "crime.boss": _("Criminal leadership"),
        "crime.terror": _("Terrorism"),
        "crime.traffick": _("Trafficking"),
        "crime.traffick.drug": _("Drug trafficking"),
        "crime.traffick.human": _("Human trafficking"),
        "forced.labor": _("Forced labor"),
        "asset.frozen": _("Frozen asset"),
        "wanted": _("Wanted"),
        "corp.offshore": _("Offshore"),
        "corp.shell": _("Shell company"),
        "corp.public": _("Public listed company"),
        "corp.disqual": _("Disqualified"),
        "gov": _("Government"),
        "gov.national": _("National government"),
        "gov.state": _("State government"),
        "gov.muni": _("Municipal government"),
        "gov.soe": _("State-owned enterprise"),
        "gov.igo": _("Intergovernmental organization"),
        "gov.head": _("Head of government or state"),
        "gov.admin": _("Civil service"),
        "gov.executive": _("Executive branch of government"),
        "gov.legislative": _("Legislative branch of government"),
        "gov.judicial": _("Judicial branch of government"),
        "gov.security": _("Security services"),
        "gov.financial": _("Central banking and financial integrity"),
        "fin": _("Financial services"),
        "fin.bank": _("Bank"),
        "fin.fund": _("Fund"),
        "fin.adivsor": _("Financial advisor"),
        "reg.action": _("Regulator action"),
        "reg.warn": _("Regulator warning"),
        "role.pep": _("Politician"),
        "role.pol": _("Non-PEP"),
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
        "role.lobby": _("Lobbyist"),
        "pol.party": _("Political party"),
        "pol.union": _("Union"),
        "rel": _("Religion"),
        "mil": _("Military"),
        "sanction": _("Sanctioned entity"),
        "sanction.linked": _("Sanction-linked entity"),
        "sanction.counter": _("Counter-sanctioned entity"),
        "export.control": _("Export controlled"),
        "export.risk": _("Trade risk"),
        "debarment": _("Debarred entity"),
        "poi": _("Person of interest"),
    }

    def _locale_names(self, locale: Locale) -> EnumValues:
        return {k: gettext(v) for (k, v) in self._TOPICS.items()}
