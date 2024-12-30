# crm_flask/app/models/tasks.py
from ..extensions import db
from datetime import datetime


class Tasks(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    status = db.relationship('TaskStatuses', backref='tasks', lazy='joined')
    priority = db.relationship('TaskPriorities', backref='tasks', lazy='joined')
    task_type = db.relationship('TaskTypes', backref='related_tasks', lazy='joined')
    created_user = db.relationship('Users', foreign_keys=[created_by], backref='created_tasks')

    # Добавляем связь для получения division_id из task_type
    task_division = db.relationship('Divisions', secondary='task_types', backref='task_divisions', lazy='joined')
    # Subtasks relationship
    subtasks = db.relationship('Tasks', backref=db.backref('parent_task', remote_side=[id]), lazy='dynamic')
