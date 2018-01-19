from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gsapi.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.app_context().push()
    return app


app = create_app()

#   read config
with open('config.json', encoding='utf-8') as f:
    config = json.load(f)


class Link(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    # needs
    engine_name = db.Column(db.String)
    data = db.Column(db.Text)
    # sets
    redirect = db.Column(db.String, default=None)
    done = db.Column(db.Boolean, default=False)
    working = db.Column(db.Boolean, default=False)

    def __init__(self, e: str, data: dict):
        self.engine_name = e
        self.data = json.dumps(data)

    @property
    def response(self):
        return dict(link_id=self.id, data=self.data)

    @classmethod
    def get_to_do(cls, e: str):
        return cls.query.filter_by(engine_name=e, working=False, done=False).first()

    @classmethod
    def get_by_id(cls, id_):
        return cls.query.filter_by(id=id_).first()

    def insert(self):
        db.session.add(self)
        db.session.commit()
        return self

    def set_working(self):
        self.working = True
        db.session.commit()

    def set_not_working(self):
        self.working = False
        db.session.commit()

    def set_redirect(self, r: str):
        self.redirect = r
        self.done = True
        self.working = False
        db.session.commit()


# CREATOR = GSA Search Engine Ranker
# CONSUMER = YOUR SCRIPT

# INDEX GET
@app.route('/')
def index():
    return jsonify(dict(success=True, results='Server works just fine :)'))


# CREATOR posts to this url:
@app.route('/api/link/create/<path:e>', methods=['POST'])
def post_link(e):
    try:
        _l = Link(e, request.json).insert()
        return jsonify(dict(success=True, results=_l.response))
    except Exception as _error:
        return jsonify(dict(success=False, results=repr(_error)))


# CONSUMER get's link data here:
@app.route('/api/link/consume/<path:e>')
def consume_link(e):
    try:
        _l = Link.get_to_do(e)
        if _l is None:
            return jsonify(dict(success=False, results=f"No tasks for {e}"))
        if _l:
            _l.set_working()
            return jsonify(dict(success=True, results=_l.response))
    except Exception as _error:
        return jsonify(dict(success=False, results=repr(_error)))


# CONSUMER set's link redirect here:
@app.route('/api/link/set_redirect/<int:id_>/<path:r>')
def set_redirect(id_, r):
    try:
        _l = Link.get_by_id(id_)
        if _l is None:
            return jsonify(dict(success=False, results=f"No task with id: {id_}"))
        if _l:
            _l.set_redirect(r)
            return jsonify(dict(success=True, results=_l.response))
    except Exception as _error:
        return jsonify(dict(success=False, results=repr(_error)))


# CREATOR verifies link data here
@app.route('/api/link/verify_redirect/<int:id_>')
def verify_redirect(id_):
    try:
        _l = Link.get_by_id(id_)
        if _l.redirect:
            return redirect(_l.redirect, 301)
        if _l is None:
            return jsonify(dict(success=False, results=f"No tasks for id: {id_}"))
        if _l.redirect is None:
            return jsonify(dict(success=False, results=f"Redirect is none..."))
    except Exception as _error:
        return jsonify(dict(success=False, results=repr(_error)))


# CONSUMER marks link as not working, in case of errors (it makes possible to consume this link again)
@app.route('/api/link/set_not_working/<int:id_>')
def set_not_working(id_):
    try:
        _l = Link.get_by_id(id_)
        if _l is None:
            return jsonify(dict(success=False, results=f"No tasks for id: {id_}"))
        if _l:
            _l.set_not_working()
            return jsonify(dict(success=True, results=_l.response))
    except Exception as _error:
        return jsonify(dict(success=False, results=repr(_error)))


if __name__ == '__main__':
    db.create_all()
    app.run(
        threaded=True,
        host=config['gsapi_server']['host'],
        port=config['gsapi_server']['port'])
