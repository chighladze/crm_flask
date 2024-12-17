# crm_flask/app/models/task_types.py
from datetime import datetime
from ..extensions import db

class TaskTypes(db.Model):
    __tablename__ = 'task_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    division_id = db.Column(db.Integer, db.ForeignKey('divisions.id'), nullable=False)

    division = db.relationship('Divisions', backref='task_types')

    def __repr__(self):
        return f"<TaskType {self.name}>"
