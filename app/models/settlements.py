from datetime import datetime

from ..extensions import db


class Settlement(db.Model):
    __tablename__ = 'settlements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=False)

    district = db.relationship('District', back_populates='settlements')
