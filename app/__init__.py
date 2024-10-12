from flask import Flask, session
from flask_session import Session
from flask_login import current_user
from .extensions import db, migrate, login_manager, csrf
from .config import Config
from datetime import datetime
import pytz

from .routes.users import users
from .routes.dashboard import dashboard
from .routes.map import map
from .routes.error import error
from .routes.api import api
from .routes.departments import departments
from .routes.department_positions import department_positions
from .routes.divisions import divisions
from .routes.nms import nms
from .routes.roles import roles
from .routes.customers import customers


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

    # Инициализация сессии
    Session(app)

    app.jinja_env.globals['now'] = datetime.now

    app.register_blueprint(users)
    app.register_blueprint(dashboard)
    app.register_blueprint(map)
    app.register_blueprint(error)
    app.register_blueprint(api)
    app.register_blueprint(departments)
    app.register_blueprint(department_positions)
    app.register_blueprint(divisions)
    app.register_blueprint(nms)
    app.register_blueprint(roles)
    app.register_blueprint(customers)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # LOGIN MANAGER
    login_manager.login_view = 'users.login'
    login_manager.login_message = False

    with app.app_context():
        db.create_all()

    return app
