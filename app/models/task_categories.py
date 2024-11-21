# crm_flask/app/models/task_categories.py
from ..extensions import db


class TaskCategories(db.Model):
    __tablename__ = 'task_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    position_id = db.Column(db.Integer, db.ForeignKey('division_positions.id'), nullable=True)

    # Связь с моделью DivisionPositions
    division_position = db.relationship("DivisionPositions", back_populates="task_categories")
    tasks = db.relationship('Tasks', back_populates='task_category')
    task_types = db.relationship("TaskTypes", back_populates="task_category", lazy='joined')


    def __repr__(self):
        return f'<TaskCategory {self.name}>'
