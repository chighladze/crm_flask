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

    # Relationship the Departments model
    department = db.relationship('Departments', backref=db.backref('divisions', cascade='all, delete'))

    def __repr__(self):
        return f'<Division {self.name}>'


