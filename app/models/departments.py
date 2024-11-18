# crm_flask/app/models/departments.py
from ..extensions import db
from datetime import datetime


class Departments(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь с Divisions
    divisions = db.relationship('Divisions', back_populates='department', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Department {self.name}>'
