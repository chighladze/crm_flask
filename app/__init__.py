from flask import Flask, session
from flask_session import Session
from flask_login import current_user
from .extensions import db, migrate, login_manager, csrf
from .config import Config
from datetime import datetime
import pytz
from .routes import register_routes


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.before_request
    def update_last_activity():
        if current_user.is_authenticated:
            tz_tbilisi = pytz.timezone('Asia/Tbilisi')
            current_user.last_activity = datetime.now(tz_tbilisi)
            db.session.commit()

    csrf.init_app(app)
    Session(app)
    app.jinja_env.globals['now'] = datetime.now
    register_routes(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    # LOGIN MANAGER
    login_manager.login_view = 'users.login'
    login_manager.login_message = False

    with app.app_context():
        db.create_all()

    return app
