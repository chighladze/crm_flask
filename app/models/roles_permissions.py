# crm_flask/app/models/roles_permissions.py
from ..extensions import db
from datetime import datetime


class RolesPermissions(db.Model):
    __tablename__ = 'roles_permissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
