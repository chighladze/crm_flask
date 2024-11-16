# crm_flask/app/models/customers_type.py
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

    # Relationship with TariffPlan model
    tariff_plans = db.relationship('TariffPlan', back_populates='customer_type')
    customers = db.relationship('Customers', back_populates='customer_type', lazy='select')
