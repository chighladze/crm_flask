from ..extensions import db


class TaskCategories(db.Model):
    __tablename__ = 'task_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
