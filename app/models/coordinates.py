# crm_flask/app/models/coordinates.py
from ..extensions import db
from datetime import datetime


class Coordinates(db.Model):
    __tablename__ = 'coordinates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Numeric(10, 8), nullable=True)
    longitude = db.Column(db.Numeric(11, 8), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
