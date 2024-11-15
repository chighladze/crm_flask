# crm_flask/app/models/users_roles.py:
from ..extensions import db
from datetime import datetime


class UsersRoles(db.Model):
    __tablename__ = 'users_roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('Users', backref='roles', lazy=True)
    role = db.relationship('Roles', backref='users', lazy=True)

    def __repr__(self):
        return f'<UserRole User ID: {self.user_id}, Role ID: {self.role_id}>'
