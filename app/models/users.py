from ..extensions import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.exc import SQLAlchemyError


class Users(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    passwordHash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default='1', nullable=False)
    lastLogin = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, nullable=True)
    failedLoginAttempts = db.Column(db.Integer, default=0)
    lockOutUntil = db.Column(db.DateTime, default=datetime.utcnow)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, str(user_id))


class UserLog(db.Model):
    __tablename__ = 'user_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Функция для создания записи в логе
def log_action(user, action):
    log = UserLog(user_id=user.id, action=action)
    try:
        db.session.add(log)
        db.session.commit()
        print("Запись в лог успешно добавлена.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Ошибка при добавлении записи в лог: {e}")

