from ..extensions import db
from datetime import datetime


class Coordinates(db.Model):
    __tablename__ = 'coordinates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
