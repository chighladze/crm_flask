from ..extensions import db
from datetime import datetime


class TariffPlan(db.Model):
    __tablename__ = 'tariff_plans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # Название тарифа
    customer_type_id = db.Column(db.Integer, db.ForeignKey('customers_type.id'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Цена тарифа
    currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'), nullable=False)  # Ссылка на валюту
    technology_id = db.Column(db.Integer, db.ForeignKey('connection_technology.id'),
                              nullable=False)  # Ссылка на технологию подключения

    internet_download_speed = db.Column(db.Integer)  # Скорость скачивания
    internet_upload_speed = db.Column(db.Integer)  # Скорость отправки
    internet_min_download_speed = db.Column(db.Integer)  # Минимальная скорость скачивания
    internet_min_upload_speed = db.Column(db.Integer)  # Минимальная скорость отправки
    internet_data_limit = db.Column(db.Integer)  # Лимит данных
    internet_unlimited = db.Column(db.Boolean, default=False)  # Безлимитный интернет

    # tv_service = db.Column(db.Boolean, default=False)  # Наличие ТВ-сервиса
    # tv_channels = db.Column(db.Integer)  # Количество каналов
    # tv_hd_channels = db.Column(db.Integer)  # Количество HD-каналов
    # tv_package_id = db.Column(db.Integer, db.ForeignKey('tv_packages.id'))  # Ссылка на пакет ТВ
    # tv_movie_rentals = db.Column(db.Boolean, default=False)  # Наличие аренды фильмов
    #
    # phone_service = db.Column(db.Boolean, default=False)  # Наличие телефонного сервиса
    # phone_minutes = db.Column(db.Integer)  # Количество минут в пакете
    # phone_international = db.Column(db.Boolean, default=False)  # Международные звонки
    # phone_voicemail = db.Column(db.Boolean, default=False)  # Голосовая почта
    # phone_call_forwarding = db.Column(db.Boolean, default=False)  # Переадресация звонков
    #
    # mobile_app_support = db.Column(db.Boolean, default=False)  # Поддержка мобильного приложения
    # priority_support = db.Column(db.Boolean, default=False)  # Приоритетная поддержка
    # equipment_rental = db.Column(db.Boolean, default=False)  # Аренда оборудования
    # equipment_discount = db.Column(db.Numeric(5, 2))  # Скидка на аренду оборудования
    # discount_amount = db.Column(db.Numeric(10, 2))  # Сумма скидки
    # discount_duration = db.Column(db.Integer)  # Длительность скидки
    #
    # time_restriction_start = db.Column(db.Time)  # Время начала ограничений
    # time_restriction_end = db.Column(db.Time)  # Время окончания ограничений
    description = db.Column(db.Text)  # Описание тарифа
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Дата создания
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                           nullable=False)  # Дата обновления

    # Определение отношений с другими таблицами
    connection_technology = db.relationship('ConnectionTechnology', back_populates='tariff_plans')
    customer_type = db.relationship('CustomersType', back_populates='tariff_plans')
    currency = db.relationship('Currencies', back_populates='tariff_plans')
    technology = db.relationship('ConnectionTechnology', back_populates='tariff_plans')
    # tv_package = db.relationship('TVPackage', back_populates='tariff_plans')

