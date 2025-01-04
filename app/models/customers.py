# crm_flask/app/models/customers.py
from ..extensions import db
from datetime import datetime


class Customers(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_id = db.Column(db.Integer, db.ForeignKey('customers_type.id'), nullable=False)
    identification_number = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    director = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    mobile = db.Column(db.String(20), nullable=True)
    mobile_second = db.Column(db.String(20), nullable=True)
    resident = db.Column(db.Boolean, default=True, nullable=False)
    legal_address = db.Column(db.String, nullable=False)
    actual_address = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define the relationship with the CustomersType model
    customer_type = db.relationship('CustomersType', back_populates='customers', lazy='joined')
    # Relationships
    customer_accounts = db.relationship('CustomerAccount', back_populates='customer')

    def __repr__(self):
        return f"<Customer {self.name}>"
