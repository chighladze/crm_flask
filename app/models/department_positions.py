from ..extensions import db
from datetime import datetime


class DepartmentPositions(db.Model):
    __tablename__ = 'department_positions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    department = db.relationship('Departments', backref='positions')

    def __repr__(self):
        return f'<Division {self.name}>'
