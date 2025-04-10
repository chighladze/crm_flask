# crm_flask/app/models/task_statuses.py
from ..extensions import db


class TaskStatuses(db.Model):
    __tablename__ = 'task_statuses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    name_geo = db.Column(db.String(40), unique=True, nullable=False)
    bootstrap_class = db.Column(db.String(50), unique=True, nullable=True)
