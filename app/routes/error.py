# crm_flask/app/routes/error.py

from flask import Blueprint, render_template, flash
import jinja2

error = Blueprint('error', __name__)


@error.app_errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


@error.app_errorhandler(500)
def internal_server_error(e):
    flash("სერვერზე მოხდა შეცდომა.", "danger")
    return render_template('error/500.html'), 500


# Add this handler for UndefinedError
@error.app_errorhandler(jinja2.exceptions.UndefinedError)
def handle_jinja_undefined_error(e):
    return render_template('error/500.html'), 500
