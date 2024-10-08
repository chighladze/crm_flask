from flask import Blueprint, abort, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from ..models.users import Users
from ..models.users_roles import UsersRoles
from ..models.roles_permissions import RolesPermissions

from ..extensions import db

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('dashboard/index.html', current_user=current_user)
