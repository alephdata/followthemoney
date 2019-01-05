import logging

from followthemoney_integrate.model import Vote, Match

log = logging.getLogger(__name__)


def tally_votes(session, updated=False):
    for (match_id, judgement, count) in Vote.tally(session, updated=updated):
        log.info("Decided: %s (%s w/ %d votes)", match_id, judgement, count)
        Match.update(session, match_id, judgement)
    session.commit()
