import os
from flask import Flask, request, render_template, redirect

from followthemoney_integrate import settings
from followthemoney_integrate.model import Session


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
