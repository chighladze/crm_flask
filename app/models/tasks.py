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
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)

    status = db.relationship('TaskStatuses', backref='tasks', lazy='joined')
    priority = db.relationship('TaskPriorities', backref='tasks', lazy='joined')
    task_type = db.relationship('TaskTypes', back_populates='related_tasks')
    created_user = db.relationship('Users', foreign_keys=[created_by], backref='created_tasks')

    # Для доступа к связанному подразделению (создания задачи)
    created_division = db.relationship('Divisions', foreign_keys=[created_division_id])

    subtasks = db.relationship('Tasks', backref=db.backref('parent_task', remote_side=[id]), lazy='dynamic')
    order = db.relationship(
        'Orders',
        backref='tasks_related',
        foreign_keys=[order_id]
    )
