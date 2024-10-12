from ..extensions import db
from datetime import datetime


class CustomersType(db.Model):
    __tablename__ = 'customers_type'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    shortName = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, default=0, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Relationship with Customers model (renamed to avoid conflict)
    customer_type = db.relationship('Customers', backref='customer_type', lazy=True)
