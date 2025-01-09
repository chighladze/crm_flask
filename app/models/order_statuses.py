# crm_flask/app/models/order_statuses.py

from ..extensions import db

class OrderStatus(db.Model):
    __tablename__ = 'order_statuses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    name_geo = db.Column(db.String(50), unique=True, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    bootstrap_class = db.Column(db.String(50), nullable=False, default='secondary')  # New attribute
    hided = db.Column(db.Boolean, default=False)

    # Relationship with Orders
    orders = db.relationship('Orders', back_populates='status')

    def __repr__(self):
        return f"<OrderStatus {self.name}>"
