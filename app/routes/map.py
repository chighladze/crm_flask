from flask import Blueprint, abort, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from ..extensions import db

map = Blueprint('map', __name__)


@map.route('/map/index/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('map/index.html'
                           , current_user=current_user
                           )

@map.route('/map/open_street_map/', methods=['GET', 'POST'])
@login_required
def open_street_map():
    return render_template('map/open_street_map.html'
                           , current_user=current_user
                           )