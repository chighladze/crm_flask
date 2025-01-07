# crm_flask/app/models/order_statuses.py

from ..extensions import db


class OrderStatus(db.Model):
    __tablename__ = 'order_statuses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Отношение с заказами
    orders = db.relationship('Orders', back_populates='status')

    def __repr__(self):
        return f"<OrderStatus {self.name}>"
