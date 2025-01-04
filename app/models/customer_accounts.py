# crm_flask/app/models/customer_accounts.py
from ..extensions import db
from datetime import datetime

class CustomerAccount(db.Model):
    __tablename__ = 'customer_accounts'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='Unique identifier for the account')
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False, comment='ID of the customer from the customers table')
    account_pay_number = db.Column(db.String(20), unique=True, nullable=False, comment='Unique payment account number')
    mac_address = db.Column(db.String(17), unique=True, nullable=False, comment='MAC address of the device')
    ip_address = db.Column(db.String(45), nullable=True, comment='IP address (can be IPv4 or IPv6)')
    tariff_plan_id = db.Column(db.Integer, db.ForeignKey('tariff_plans.id', ondelete='CASCADE'), nullable=False, comment='ID of the tariff plan')
    device_name = db.Column(db.String(100), nullable=False, comment='Name of the device (e.g., TP-Link Archer C6)')
    device_type = db.Column(db.Enum('Router', 'Modem', 'ONU', 'STB', 'Other'), nullable=False, comment='Type of the device')
    status = db.Column(db.Enum('Active', 'Inactive', 'Suspended'), default='Active', nullable=True, comment='Account status')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='Date and time of account creation')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='Date and time of last update')

    # Исправленное отношение с Orders
    order = db.relationship('Orders', back_populates='customer_account')

    # Связи с другими моделями
    customer = db.relationship('Customers', back_populates='customer_accounts')
    tariff_plan = db.relationship('TariffPlan', back_populates='customer_accounts')

    def __repr__(self):
        return f"<CustomerAccount {self.account_pay_number} - {self.mac_address}>"
