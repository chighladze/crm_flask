# crm_flask/app/routes/error.py

from flask import Blueprint, render_template, flash, current_app
import jinja2

error = Blueprint('error', __name__)


@error.app_errorhandler(404)
def page_not_found(e):
    current_app.logger.warning(f"404 Not Found: {e}")
    return render_template('error/404.html'), 404


@error.app_errorhandler(500)
def internal_server_error(e):
    flash("სერვერზე მოხდა შეცდომა.", "danger")
    current_app.logger.error(f"500 Internal Server Error: {e}", exc_info=True)
    return render_template('error/500.html'), 500


# @error.app_errorhandler(jinja2.exceptions.UndefinedError)
# def handle_jinja_undefined_error(e):
#     current_app.logger.error(f"Jinja UndefinedError: {e}", exc_info=True)
#     return render_template('error/500.html'), 500
