# crm_flask/app/models/currencies.py
from ..extensions import db
from datetime import datetime


class Currencies(db.Model):
    __tablename__ = 'currencies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Идентификатор валюты
    code = db.Column(db.String(3), nullable=False, unique=True)  # Код валюты (например, 'USD')
    name = db.Column(db.String(100), nullable=False)  # Название валюты
    symbol = db.Column(db.String(10))  # Символ валюты (например, '$')

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Дата создания
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                           nullable=False)  # Дата обновления

    tariff_plans = db.relationship('TariffPlan', back_populates='currency')

    def __repr__(self):
        return f'<Currency {self.name} ({self.code})>'
