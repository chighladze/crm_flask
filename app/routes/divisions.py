from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
import sqlalchemy as sa
from ..extensions import db
from ..forms.departments import DepartmentCreateForm
from ..models.departments import Departments

divisions = Blueprint('divisions', __name__)


@divisions.route('/departments/divisions/<int:id>', methods=['GET', 'POST'])
@login_required
def div_list(id):
    return render_template('division/list.html')