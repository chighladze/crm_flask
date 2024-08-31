from ..extensions import db, login_manager
from datetime import datetime
from flask_login import UserMixin


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    passwordHash = db.Column(db.String(255), nullable=False)
    lastLogin = db.Column(db.DateTime, default=datetime.utcnow)
    failedLoginAttempts = db.Column(db.Integer, default=0)
    lockOutUntil = db.Column(db.DateTime, default=datetime.utcnow)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
