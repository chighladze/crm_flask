# crm_flask/app/models/roles.py
from ..extensions import db
from datetime import datetime


class Roles(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Defining relationship with RolesPermissions
    permissions = db.relationship('RolesPermissions', backref='role', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Role {self.name}>'
