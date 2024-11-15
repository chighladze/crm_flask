# crm_flask/app/models/connection_technology.py
from ..extensions import db
from datetime import datetime


class ConnectionTechnology(db.Model):
    __tablename__ = 'connection_technology'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                           nullable=False)

    tariff_plans = db.relationship("TariffPlan", back_populates="connection_technology")

    def __repr__(self):
        return f'<ConnectionTechnology {self.name}>'
