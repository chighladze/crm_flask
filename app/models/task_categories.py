from ..extensions import db


class TaskCategories(db.Model):
    __tablename__ = 'task_categories'

    id = db.Column(db.Integer, primary_key=True)
    division_position_id = db.Column(db.Integer, db.ForeignKey('division_positions.id'), nullable=True)

    division_position = db.relationship("DivisionPositions", back_populates="task_categories")

    def __repr__(self):
        return f'<TaskCategory {self.id}>'