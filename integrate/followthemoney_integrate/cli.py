import sys
import click
import logging

from followthemoney.dedupe import Recon
from followthemoney.cli.util import read_entity
from followthemoney_enrich.cli import read_result
from followthemoney_integrate.views import app
from followthemoney_integrate.model import metadata, Session, Entity
from followthemoney_integrate.model import Match, Vote


@click.group(help="Utility for the FollowTheMoney integration tool")
def cli():
    fmt = '%(name)s [%(levelname)s] %(message)s'
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=fmt)


@cli.command('init', help="Initalise database")
@click.option('--drop/--no-drop', default=False)
def init(drop):
    if drop:
        metadata.drop_all()
    metadata.create_all()


@cli.command('load-entities', help="Load entities")
@click.option('-e', '--entities', type=click.File('r'), default='-')  # noqa
def load_entities(entities):
    session = Session()
    try:
        while True:
            entity = read_entity(entities)
            if entity is None:
                break
            Entity.save(session, entities.name, entity)
    except BrokenPipeError:
        pass
    session.commit()


@cli.command('load-results', help="Load results")
@click.option('-r', '--results', type=click.File('r'), default='-')  # noqa
def load_results(results):
    session = Session()
    try:
        while True:
            result = read_result(results)
            if result is None:
                break
            if result.subject is None or result.candidate is None:
                continue
            se = Entity.save(session, result.enricher.name, result.subject)
            ce = Entity.save(session, result.enricher.name, result.candidate)
            priority = max((se.priority, ce.priority))
            Match.save(session, result.subject, result.candidate,
                       score=result.score, priority=priority)
            session.flush()
    except BrokenPipeError:
        pass
    session.commit()


@cli.command('load-recon', help="Import recon judgements")
@click.option('-r', '--recon', type=click.File('r'), default='-')  # noqa
def load_recon(recon):
    session = Session()
    for recon in Recon.from_file(recon):
        Match.save(session, recon.subject, recon.canonical,
                   judgement=recon.judgement)
    session.commit()


@cli.command('dump-recon', help="Export recon judgements")
@click.option('-r', '--recon', type=click.File('w'), default='-')  # noqa
def dump_recon(recon):
    session = Session()
    Match.tally(session)
    session.commit()
    for match in Match.all(session):
        if match.judgement is not None:
            obj = Recon(match.subject, match.candidate, match.judgement)
            recon.write(obj.to_json())
            recon.write('\n')
            recon.flush()


@cli.command('load-votes', help="Import individual votes")
@click.option('-v', '--votes', type=click.File('r'), default='-')  # noqa
def load_votes(votes):
    session = Session()
    try:
        while True:
            data = read_entity(votes)
            if data is None:
                break
            Vote.save(session,
                      data.get('match_id'),
                      data.get('user'),
                      data.get('judgement'))
    except BrokenPipeError:
        pass
    Match.tally(session)
    session.commit()


@cli.command('dump-votes', help="Export individual votes")
@click.option('-v', '--votes', type=click.File('w'), default='-')  # noqa
def dump_votes(votes):
    session = Session()
    for vote in Vote.all(session):
        votes.write(vote.to_json())
        votes.write('\n')
        votes.flush()


@cli.command('dedupe', help="Perform ultra-slow internal de-duplication")
@click.option('-t', '--threshold', type=float, default=0.5)
def dedupe(threshold):
    session = Session()
    Entity.dedupe(session, threshold=threshold)
    session.commit()


@cli.command('serve')
def serve():
    app.debug = True
    app.run(host='0.0.0.0')
