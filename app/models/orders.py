from ..extensions import db
from datetime import datetime


class Orders(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    settlement_id = db.Column(db.Integer, db.ForeignKey('settlement.id'))
    building_type_id = db.Column(db.Integer, db.ForeignKey('building_types.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    coordinate_id = db.Column(db.Integer, db.ForeignKey('coordinates.id'))
    registry_code = db.Column(db.String(100))
    mobile = db.Column(db.String(20), nullable=False)
    alt_mobile = db.Column(db.String(20))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
