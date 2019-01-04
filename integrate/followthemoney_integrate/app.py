import os
import json

from flask import Flask, request, render_template, redirect

app = Flask(__name__)


def get_user_name():
    return request.headers.get("KEYCLOAK_USERNAME") or 'anonymous'


def increment_field(data, field):
    if data[field] is None:
        data[field] = 0
    data[field] += 1
    return data


def get_matches(query):
    match_table = db['zz_enrich_match']
    matches = list(db.query(query))
    if matches:
        match = matches[0]
        entity_id = match['entity_id']
        matches = list(match_table.find(entity_id=entity_id))
    else:
        matches = []
    return matches


@app.route('/')
def index():
    return redirect('/task/')


@app.route('/task/', methods=["GET", "POST"])
def task():
    user_name = get_user_name()
    if request.method == 'GET':
        # Get a candidate with less than 2 votes and one that the current user
        # has not seen yet
        query = """SELECT m.candidate_id, m.entity_id
                FROM zz_enrich_match m
                WHERE (m.total_votes IS Null OR m.total_votes < 2)
                AND NOT EXISTS
                (SELECT * FROM zz_enrich_votes v
                WHERE v.user_id = '{0}'
                AND v.candidate_id = m.candidate_id)
                LIMIT 1""".format(user_name)
        matches = get_matches(query)
        entity = {}
        if not matches:
            # Is there any task that needs a tie-breaker?
            # Tie-break task shows all potential matches again; as opposed to
            # only the ones that need tie-breaking 
            query = """SELECT m.candidate_id, m.entity_id
            FROM zz_enrich_match m
            WHERE (m.total_votes > 1 AND m.yes == m.no)
            AND NOT EXISTS
            (SELECT * FROM zz_enrich_votes v
            WHERE v.user_id = '{0}'
            AND v.candidate_id = m.candidate_id)
            LIMIT 1""".format(user_name)
            matches = get_matches(query)
        if matches:
            for match in matches:
                match["candidate_data"] = json.loads(match["candidate_data"])
            entity["entity_data"] = json.loads(matches[0]["entity_data"])
        ctx = {
            "matches": matches,
            "entity": entity
        }
        return render_template("task.html", **ctx)
    if request.method == 'POST':
        votes = request.form
        for candidate_id in votes:
            with db as tx:
                match_table = tx['zz_enrich_match']
                match = match_table.find_one(candidate_id=candidate_id)
                vote = votes[candidate_id]
                assert vote in ('yes', 'no', 'maybe')
                match = increment_field(match, 'total_votes')
                match = increment_field(match, vote)
                match_table.upsert(match, ['candidate_id'])
                votes_table = tx['zz_enrich_votes']
                votes_table.insert({
                    'candidate_id': candidate_id,
                    'user_id': user_name,
                    'vote': vote,
                })

        return redirect('/task/')


if __name__ == '__main__':
    init()
    app.run()
