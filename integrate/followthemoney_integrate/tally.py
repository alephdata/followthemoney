import logging

from followthemoney_integrate.model import Vote

log = logging.getLogger(__name__)


def tally_votes(session):
    Vote.tally(session)
