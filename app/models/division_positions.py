from ..extensions import db
from datetime import datetime


class DivisionPositions(db.Model):
    __tablename__ = 'division_positions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    division_id = db.Column(db.Integer, db.ForeignKey('divisions.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    division = db.relationship('Divisions', backref='positions')
    task_categories = db.relationship("TaskCategories", back_populates="division_position")

    def __repr__(self):
        return f'<Division Position {self.name}>'
