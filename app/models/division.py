# crm_flask/app/models/divisions.py
from ..extensions import db
from datetime import datetime


class Divisions(db.Model):
    __tablename__ = 'divisions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship with Departments model
    department = db.relationship('Departments', back_populates='divisions')

    def __repr__(self):
        return f'<Division {self.name}>'
