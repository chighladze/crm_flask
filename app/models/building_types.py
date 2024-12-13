# crm_flask/app/models/building_types.py
from ..extensions import db


class BuildingType(db.Model):
    __tablename__ = 'building_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

