# crm_flask/app/models/permissions.py
from ..extensions import db
from datetime import datetime

class Permissions(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Defining relationship with RolesPermissions
    roles_permissions = db.relationship('RolesPermissions', backref='permission', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Permission {self.name}>'