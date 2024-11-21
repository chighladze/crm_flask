# crm_flask/app/models/task_types.py
from ..extensions import db


class TaskTypes(db.Model):
    __tablename__ = 'task_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('task_categories.id'), nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relationship with TaskCategories
    task_category = db.relationship("TaskCategories", back_populates="task_types")
