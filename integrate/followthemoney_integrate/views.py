import os
from flask import Flask, url_for, request, render_template, redirect, abort

from followthemoney_integrate import settings
from followthemoney_integrate.model import Session, Match, Entity, Vote


dir_name = os.path.dirname(__file__)
app = Flask('ftmintegrate',
            static_folder=os.path.join(dir_name, 'static'),
            template_folder=os.path.join(dir_name, 'templates'))


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
        'project': settings.PROJECT_NAME
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/next')
def next_entity():
    entity_id = Entity.by_priority(request.session, request.user)
    if entity_id is None:
        return redirect(url_for('index'))
    return redirect(url_for('entity', entity_id=entity_id))


@app.route('/entity/<entity_id>')
def entity(entity_id):
    entity = Entity.by_id(request.session, entity_id)
    if entity is None:
        return abort(404)
    return render_template('entity.html', entity=entity.proxy)
