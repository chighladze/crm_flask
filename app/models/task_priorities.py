# crm_flask/app/models/task_priorities.py
from ..extensions import db


class TaskPriorities(db.Model):
    __tablename__ = 'task_priorities'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level = db.Column(db.String(20), unique=True, nullable=False)
