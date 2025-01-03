# crm_flask/app/models/orders.py
from ..extensions import db
from datetime import datetime


class Orders(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    alt_mobile = db.Column(db.String(20))
    tariff_plan_id = db.Column(db.Integer, db.ForeignKey('tariff_plans.id'))
    comment = db.Column(db.Text(255), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    legal_address = db.Column(db.String, nullable=False)
    actual_address = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = db.relationship('Customers', backref='orders', lazy='joined')
    tariff_plan = db.relationship('TariffPlan', backref='orders', lazy='joined')
    # Add this relationship
    address = db.relationship('Addresses', backref='orders', lazy='joined')
    task = db.relationship('Tasks', backref='orders', lazy='joined')