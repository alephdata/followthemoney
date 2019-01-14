import os
import logging
from flask import Flask, url_for, request, render_template, redirect, abort

from followthemoney_integrate import settings
from followthemoney_integrate.model import Session, Match, Entity, Vote

log = logging.getLogger(__name__)
dir_name = os.path.dirname(__file__)
app = Flask('ftmintegrate',
            static_folder=os.path.join(dir_name, 'static'),
            template_folder=os.path.join(dir_name, 'templates'))


def score_class(score):
    if score > 0.9:
        return 'table-success'
    if score > 0.7:
        return 'table-warning'
    if score > 0.0:
        return 'table-danger'


def valued_checked(value, checked):
    text = 'value="%s" ' % value
    if value == checked:
        text += 'checked="checked"'
    return text


@app.before_request
def before():
    request.session = Session()
    request.user = 'anonymous'
    request.user = request.headers.get("KEYCLOAK_USERNAME") or request.user


@app.after_request
def after(resp):
    request.session.rollback()
    request.session.close()
    return resp


@app.context_processor
def template_context():
    return {
        'user': request.user,
        'project': settings.PROJECT_NAME,
        'score_class': score_class,
        'valued_checked': valued_checked
    }


@app.route('/')
def index():
    return redirect(url_for('search'))


@app.route('/search')
def search():
    query = request.args.get('q')
    q = Entity.by_search(request.session, query)
    q = q.limit(100)
    return render_template('search.html', results=q, query=query)


@app.route('/next')
def next_entity():
    entity_id = Entity.by_priority(request.session, request.user)
    if entity_id is None:
        return redirect(url_for('index'))
    return redirect(url_for('entity', entity_id=entity_id))


@app.route('/vote', methods=['POST', 'PUT'])
def vote():
    action = request.form.get('action', 'next')
    for match_id, judgement in request.form.items():
        if match_id == 'action':
            continue
        log.info("[%s] voted %s on %s", request.user,
                 judgement, match_id)
        Vote.save(request.session, match_id, request.user, judgement)
    Match.tally(request.session, updated=True)
    request.session.commit()
    if action == 'next':
        return redirect(url_for('next_entity'))
    return redirect(url_for('entity', entity_id=action))


def common_properties(entity, candidate):
    properties = []
    for prop in candidate.schema.sorted_properties:
        values = candidate.get(prop)
        if len(values):
            other = entity.get(prop, quiet=True)
            score = prop.type.compare_sets(values, other)
            properties.append({
                'prop': prop,
                'entity': other,
                'candidate': values,
                'score': score
            })
    return properties


@app.route('/entity/<entity_id>')
def entity(entity_id):
    entity = Entity.by_id(request.session, entity_id)
    if entity is None:
        return abort(404)
    votes = Vote.by_entity(request.session, request.user, entity_id)
    matches = []
    for (match, candidate) in Match.by_entity(request.session, entity_id):
        matches.append({
            'id': match.id,
            'score': match.score,
            'candidate': candidate.proxy,
            'properties': common_properties(entity.proxy, candidate.proxy),
            'judgement': votes.get(candidate.id, '?')
        })
    return render_template('entity.html',
                           entity=entity.proxy,
                           matches=matches)
