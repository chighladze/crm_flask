from flask import Blueprint, abort, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from ..extensions import db

error = Blueprint('error', __name__)


@error.errorhandler(404)
# @login_required
def page_not_found():
    return render_template('error/404.html'
                           # , current_user=current_user
                           ), 404
