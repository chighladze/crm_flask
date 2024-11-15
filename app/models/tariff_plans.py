# crm_flask/app/models/tariff_plans.py
from ..extensions import db
from datetime import datetime


class TariffPlan(db.Model):
    __tablename__ = 'tariff_plans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    customer_type_id = db.Column(db.Integer, db.ForeignKey('customers_type.id'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'), nullable=False)
    technology_id = db.Column(db.Integer, db.ForeignKey('connection_technology.id'),
                              nullable=False)

    internet_download_speed = db.Column(db.Integer)
    internet_upload_speed = db.Column(db.Integer)
    internet_min_download_speed = db.Column(db.Integer)
    internet_min_upload_speed = db.Column(db.Integer)
    internet_data_limit = db.Column(db.Integer)
    internet_unlimited = db.Column(db.Boolean, default=False)

    # tv_service = db.Column(db.Boolean, default=False)
    # tv_channels = db.Column(db.Integer)
    # tv_hd_channels = db.Column(db.Integer)
    # tv_package_id = db.Column(db.Integer, db.ForeignKey('tv_packages.id'))
    # tv_movie_rentals = db.Column(db.Boolean, default=False)
    #
    # phone_service = db.Column(db.Boolean, default=False)
    # phone_minutes = db.Column(db.Integer)
    # phone_international = db.Column(db.Boolean, default=False)
    # phone_voicemail = db.Column(db.Boolean, default=False)
    # phone_call_forwarding = db.Column(db.Boolean, default=False)
    #
    # mobile_app_support = db.Column(db.Boolean, default=False)
    # priority_support = db.Column(db.Boolean, default=False)
    # equipment_rental = db.Column(db.Boolean, default=False)
    # equipment_discount = db.Column(db.Numeric(5, 2))
    # discount_amount = db.Column(db.Numeric(10, 2))
    # discount_duration = db.Column(db.Integer)
    #
    # time_restriction_start = db.Column(db.Time)
    # time_restriction_end = db.Column(db.Time)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                           nullable=False)

    connection_technology = db.relationship(
        'ConnectionTechnology',
        back_populates='tariff_plans',
        overlaps='technology'
    )
    customer_type = db.relationship('CustomersType', back_populates='tariff_plans')
    currency = db.relationship('Currencies', back_populates='tariff_plans')
    technology = db.relationship(
        'ConnectionTechnology',
        back_populates='tariff_plans',
        overlaps='connection_technology'
    )
    # tv_package = db.relationship('TVPackage', back_populates='tariff_plans')
