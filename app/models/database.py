from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class StoredGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(80), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    min_rounds = db.Column(db.Integer, nullable=False)
    max_rounds = db.Column(db.Integer, nullable=False)
    min_turns = db.Column(db.Integer, nullable=False)
    max_turns = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    started = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'))

class StoredBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(80), db.ForeignKey('stored_game.game_id'))
    name = db.Column(db.String(80), nullable=False)
    code = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class StoredInvite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    game_id = db.Column(db.String(80), db.ForeignKey('stored_game.game_id'))
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)