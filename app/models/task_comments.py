# crm_flask/app/models/task_comments.py
from datetime import datetime
from ..extensions import db


class TaskComments(db.Model):
    __tablename__ = 'task_comments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Используем back_populates вместо backref
    task = db.relationship('Tasks', back_populates='comments')
    user = db.relationship('Users', back_populates='comments')

    def __repr__(self):
        return f"<TaskComment {self.id} by User {self.user_id}>"
