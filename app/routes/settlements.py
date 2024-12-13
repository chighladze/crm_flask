# crm_flask/app/routes/settlements.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, send_file, jsonify
from ..forms.roles import RoleCreateForm
from ..models.settlements import Settlement

settlements = Blueprint('settlements', __name__)


@settlements.route('/settlements/<int:district_id>', methods=['GET'])
def get_settlements(district_id):
    settlements = Settlement.query.filter_by(district_id=district_id).all()
    return jsonify([{'id': settlement.id, 'name': settlement.name} for settlement in settlements])
