from app.extensions import db

FIXTURES = ['User', 'Tool']


class User (db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))


class Tool(db.Model):

    __tablename__ = 'tools'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    added = db.Column(db.Date, default=None)
    last_seen = db.Column(db.DateTime, default=None)
