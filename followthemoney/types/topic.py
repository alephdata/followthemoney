from rdflib import URIRef

from followthemoney.types.common import EnumType
from followthemoney.util import gettext, defer as _


class TopicType(EnumType):
    name = 'topic'
    group = 'topics'
    label = _('Topic')
    plural = _('Topics')
    matchable = False

    _TOPICS = {
        'crime': _('Crime'),
        'crime.fraud': _('Fraud'),
        'crime.cyber': _('Cybercrime'),
        'crime.fin': _('Financial crime'),
        'crime.theft': _('Theft'),
        'crime.war': _('War crimes'),
        'crime.boss': _('Criminal leadership'),
        'crime.terror': _('Terrorism'),
        'crime.traffick': _('Trafficking'),
        'crime.traffick.drug': _('Drug trafficking'),
        'crime.traffick.human': _('Human trafficking'),
        'corp.offshore': _('Offshore'),
        'corp.shell': _('Shell company'),
        'gov': _('Government'),
        'gov.national': _('National government'),
        'gov.state': _('State government'),
        'gov.muni': _('Municipal government'),
        'gov.soe': _('State-owned enterprise'),
        'gov.igo': _('Intergovernmental organization'),
        'fin': _('Financial services'),
        'fin.bank': _('Bank'),
        'fin.fund': _('Fund'),
        'fin.adivsor': _('Financial advisor'),
        'role.pep': _('Politician'),  # don't FATF-splain me, bro.
        'role.rca': _('Associate'),
        'role.judge': _('Judge'),
        'role.civil': _('Civil servant'),
        'role.diplo': _('Diplomat'),
        'role.lawyer': _('Lawyer'),
        'role.acct': _('Accountant'),
        'role.spy': _('Spy'),
        'role.journo': _('Journalist'),
        'role.act': _('Activist'),
        'pol.party': _('Political party'),
        'pol.union': _('Union'),
        'rel': _('Religion'),
        'mil': _('Military'),
        'asset.frozen': _('Frozen asset'),
        'ctx.sanctioned': _('Sanctioned entity'),
        'ctx.poi': _('Person of interest'),
    }

    def _locale_names(self, locale):
        return {k: gettext(v) for (k, v) in self._TOPICS.items()}

    def rdf(self, value):
        return URIRef('ftm:topic:%s' % value)
