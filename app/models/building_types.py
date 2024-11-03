from ..extensions import db
from datetime import datetime


class BuildingType(db.Model):
    __tablename__ = 'building_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
