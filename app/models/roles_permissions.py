from ..extensions import db
from datetime import datetime


class RolesPermissions(db.Model):
    __tablename__ = 'roles_permissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permissions_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<RolesPermissions role_id={self.role_id}, permissions_id={self.permissions_id}>'
