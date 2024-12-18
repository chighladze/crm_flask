# crm_flask/app/models/addresses.py
from ..extensions import db
from datetime import datetime


class Addresses(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    settlement_id = db.Column(db.Integer, db.ForeignKey('settlements.id'), nullable=False)
    building_type_id = db.Column(db.Integer, db.ForeignKey('building_types.id'), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    entrance_number = db.Column(db.Integer)
    floor_number = db.Column(db.Integer)
    apartment_number = db.Column(db.Integer)
    house_number = db.Column(db.Integer)
    coordinates_id = db.Column(db.Integer, db.ForeignKey('coordinates.id'))
    registry_code = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    settlement = db.relationship('Settlement', backref='addresses')
    building_type = db.relationship('BuildingType', backref='addresses')
    coordinates = db.relationship('Coordinates', backref='addresses')

    def __repr__(self):
        return f'<Address {self.street} {self.building_number}>'

    @property
    def district(self):
        return self.settlement.district if self.settlement else None
