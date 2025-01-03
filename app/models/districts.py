# crm_flask/app/models/districts.py
from ..extensions import db
from datetime import datetime


class District(db.Model):
    __tablename__ = 'districts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    settlements = db.relationship('Settlement', back_populates='district', lazy=True)
