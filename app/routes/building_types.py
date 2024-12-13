# crm_flask/app/routes/building_types.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, send_file, jsonify
from ..forms.roles import RoleCreateForm
from ..models.building_types import BuildingType

building_types = Blueprint('building_types', __name__)


@building_types.route('/building_types', methods=['GET'])
def get_building_types():
    # Получаем все типы зданий для выбранного поселения
    building_types = BuildingType.query.all()
    return jsonify([{'id': bt.id, 'name': bt.name} for bt in building_types])
