from ..extensions import db
from datetime import datetime


class Addresses(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    settlement_id = db.Column(db.Integer, nullable=False)
    building_type_id = db.Column(db.Integer, db.ForeignKey('building_types.id'), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    building_number = db.Column(db.String(10), nullable=False)
    entrance_number = db.Column(db.Integer)
    floor_number = db.Column(db.Integer)
    apartment_number = db.Column(db.Integer)
    house_number = db.Column(db.Integer)
    coordinates_id = db.Column(db.Integer, db.ForeignKey('coordinates.id'))
    registry_code = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
