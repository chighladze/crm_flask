from ..extensions import db
from datetime import datetime


class Tasks(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_category_id = db.Column(db.Integer, db.ForeignKey('task_categories.id'))
    task_type_id = db.Column(db.Integer, db.ForeignKey('task_types.id'))
    description = db.Column(db.Text)
    status_id = db.Column(db.Integer, db.ForeignKey('task_statuses.id'), default=1)
    task_priority_id = db.Column(db.Integer, db.ForeignKey('task_priorities.id'), default=2)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_division_id = db.Column(db.Integer, db.ForeignKey('divisions.id'))
    completed_division_id = db.Column(db.Integer, db.ForeignKey('divisions.id'))
    due_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    estimated_time = db.Column(db.Integer)
    actual_time = db.Column(db.Integer)
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    comments_count = db.Column(db.Integer, default=0)
    is_recurring = db.Column(db.Boolean, default=False)